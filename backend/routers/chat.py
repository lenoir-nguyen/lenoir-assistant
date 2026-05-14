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
    For owner: retrieves relevant context from memory.
    For stranger: simple conversational response.
    """
    try:
        session_id = uuid.UUID(request.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Fetch session
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update session language if provided
    if request.language and request.language != session.language:
        session.language = request.language
        db.commit()

    # Store user message
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

    # Build appropriate chain based on session type
    if session.is_owner:
        chain, llm = build_owner_chain(db, request.language)
        # Retrieve relevant facts for context
        facts = await bulk_retrieve_facts(db, request.message, k=3)
        context = "\n".join([f"- {fact}" for fact in facts]) if facts else "No specific facts found."
        augmented_prompt = f"Relevant context about Lenoir:\n{context}\n\nUser message: {request.message}"
    else:
        chain, llm = build_stranger_chain(request.language)
        augmented_prompt = request.message

    # Stream response using SSE
    async def generate():
        """Stream tokens as SSE."""
        response_tokens = []

        try:
            # Use LLMChain to generate response
            result = await chain.apredict(input=augmented_prompt)

            # Simulate streaming by yielding tokens
            for token in result.split():
                response_tokens.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"

            # Store assistant message after streaming completes
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

            # Store embedding for owner
            if session.is_owner:
                await upsert_message_chunk(db, assistant_message.id, full_response)

            # Signal completion
            yield f"data: {json.dumps({'done': True, 'message_id': str(assistant_message.id)})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
