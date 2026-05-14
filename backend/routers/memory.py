from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

from db import get_db, Session as SessionModel, Document, PersonalFact
from services import store_chunk

router = APIRouter(prefix="/memory", tags=["memory"])


class PersonalFactRequest(BaseModel):
    """Request to add a personal fact."""
    category: str
    content: str


class PersonalFactResponse(BaseModel):
    """Response when fact is stored."""
    fact_id: str
    category: str
    content: str


class DocumentUploadResponse(BaseModel):
    """Response when document is uploaded."""
    document_id: str
    filename: str
    message: str


class PersonalFactsListResponse(BaseModel):
    """List of personal facts for a session."""
    facts: list[dict]


@router.post("/facts", response_model=PersonalFactResponse)
async def add_personal_fact(
    request: PersonalFactRequest,
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Add a structured personal fact about Lenoir.
    Only available for owner sessions.
    """
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Verify session exists and is owner
    session = db.query(SessionModel).filter(SessionModel.id == session_uuid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.is_owner:
        raise HTTPException(status_code=403, detail="Only owner can add facts")

    try:
        # Create personal fact
        fact = PersonalFact(
            category=request.category,
            content=request.content
        )
        db.add(fact)
        db.commit()
        db.refresh(fact)

        # Store as vector chunk for RAG
        await store_chunk(db, "fact", fact.id, request.content)

        return PersonalFactResponse(
            fact_id=str(fact.id),
            category=fact.category,
            content=fact.content
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add fact: {str(e)}")


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    description: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Upload a document (PDF, TXT, etc.) for the personal memory system.
    Only available for owner sessions.
    """
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Verify session exists and is owner
    session = db.query(SessionModel).filter(SessionModel.id == session_uuid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.is_owner:
        raise HTTPException(status_code=403, detail="Only owner can upload documents")

    try:
        # Read file content
        content = await file.read()

        # Create document record
        document = Document(
            filename=file.filename or "unnamed",
            description=description
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # For now, store the entire document as a chunk
        # In production, would parse PDF/TXT and chunk into smaller pieces
        text_content = content.decode('utf-8', errors='ignore')[:10000]  # Limit to 10k chars
        await store_chunk(db, "document", document.id, text_content)

        return DocumentUploadResponse(
            document_id=str(document.id),
            filename=document.filename,
            message=f"Document '{file.filename}' uploaded successfully!"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@router.get("/facts", response_model=PersonalFactsListResponse)
async def get_personal_facts(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all personal facts (owner only).
    """
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Verify session exists and is owner
    session = db.query(SessionModel).filter(SessionModel.id == session_uuid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.is_owner:
        raise HTTPException(status_code=403, detail="Only owner can view facts")

    # Fetch all facts
    facts = db.query(PersonalFact).all()

    return PersonalFactsListResponse(
        facts=[
            {
                "id": str(fact.id),
                "category": fact.category,
                "content": fact.content,
                "created_at": fact.created_at.isoformat()
            }
            for fact in facts
        ]
    )
