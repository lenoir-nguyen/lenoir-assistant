from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid
import json

from db import get_db, Session as SessionModel, Message
from services import (
    build_owner_chain,
    build_stranger_chain,
    upsert_message_chunk,
    bulk_retrieve_facts,
)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat message request."""
    session_id: str
    message: str
    language: str = "en"


class ChatResponse(BaseModel):
    """Single chat response."""
    message_id: str
    role: str
    content: str
    modality: str = "text"


@router.post("/message", response_class=StreamingResponse)
async def chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Stream chat response as SSE (Server-Sent Events).
    Owner sessions: retrieves relevant context from pgvector (RAG) before generating response.
    Stranger sessions: generates response without any personal context or history persistence.
    """
    # Validate and parse session ID
    try:
        session_id = uuid.UUID(request.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Retrieve session from database
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update session language if it differs from the request (allows per-message language switching)
    if request.language and request.language != session.language:
        session.language = request.language
        db.commit()

    # Persist user message to database for history
    user_message = Message(
        session_id=session_id,
        role="user",
        content=request.message,
        modality="text",
        language=request.language
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # Select LangChain chain and prepare prompt augmentation based on session type
    if session.is_owner:
        # Owner mode: build RAG-enhanced chain with memory and context retrieval
        chain, llm = build_owner_chain(db, request.language)
        # Retrieve top-3 similar facts from pgvector for context injection
        facts = await bulk_retrieve_facts(db, request.message, k=3)
        context = "\n".join([f"- {fact}" for fact in facts]) if facts else "No specific facts found."
        # Augment prompt with retrieved context so LLM can personalize response
        augmented_prompt = f"Relevant context about Lenoir:\n{context}\n\nUser message: {request.message}"
    else:
        # Stranger mode: simple chain with no history, no RAG, limited memory window (5 messages)
        chain, llm = build_stranger_chain(request.language)
        augmented_prompt = request.message

    # Generator function that streams response tokens via SSE
    async def generate():
        """Stream LLM response tokens to client as Server-Sent Events."""
        response_tokens = []

        try:
            # Call LLMChain.apredict() to generate response using OpenAI GPT-4o
            result = await chain.apredict(input=augmented_prompt)

            # Stream response by splitting into words and yielding as SSE data
            # Frontend receives tokens in real-time for live chat experience
            for token in result.split():
                response_tokens.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"

            # After streaming completes, persist the full response message to database
            full_response = " ".join(response_tokens)
            assistant_message = Message(
                session_id=session_id,
                role="assistant",
                content=full_response,
                modality="text",
                language=request.language
            )
            db.add(assistant_message)
            db.commit()
            db.refresh(assistant_message)

            # For owner sessions: embed the assistant response and store in pgvector for future RAG
            if session.is_owner:
                await upsert_message_chunk(db, assistant_message.id, full_response)

            # Signal end of stream with completion flag and message ID
            yield f"data: {json.dumps({'done': True, 'message_id': str(assistant_message.id)})}\n\n"

        except Exception as e:
            # Stream error back to client for error handling
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
