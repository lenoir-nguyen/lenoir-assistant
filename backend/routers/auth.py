from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db, Session as SessionModel
from services import contains_passphrase, verify_pin

router = APIRouter(prefix="/auth", tags=["auth"])


class IdentityRequest(BaseModel):
    """Identity claim message."""
    message: str
    session_id: str | None = None


class IdentityResponse(BaseModel):
    """Response to identity verification."""
    session_id: str
    is_owner: bool
    requires_pin: bool
    message: str


class PinRequest(BaseModel):
    """PIN verification request."""
    session_id: str
    pin: str


class PinResponse(BaseModel):
    """Response to PIN verification."""
    is_owner: bool
    message: str


@router.post("/identify", response_model=IdentityResponse)
async def identify(request: IdentityRequest, db: Session = Depends(get_db)):
    """
    Identify the user based on their message.
    If they claim to be Lenoir, prompt for PIN.
    Otherwise, create a stranger session.
    """
    # Check if user claims to be Lenoir
    is_lenoir_claim = contains_passphrase(request.message)

    if is_lenoir_claim:
        # Create session awaiting PIN verification
        session = SessionModel(is_owner=False, language="en")
        db.add(session)
        db.commit()
        db.refresh(session)

        return IdentityResponse(
            session_id=str(session.id),
            is_owner=False,
            requires_pin=True,
            message="I recognize you might be Lenoir! Please provide your PIN to unlock your personal memories."
        )
    else:
        # Create stranger session
        session = SessionModel(is_owner=False, language="en")
        db.add(session)
        db.commit()
        db.refresh(session)

        return IdentityResponse(
            session_id=str(session.id),
            is_owner=False,
            requires_pin=False,
            message="Hello! I'm here to chat with you. How can I help?"
        )


@router.post("/verify-pin", response_model=PinResponse)
async def verify_pin_endpoint(request: PinRequest, db: Session = Depends(get_db)):
    """Verify the PIN and unlock owner session if correct."""
    import uuid

    try:
        session_id = uuid.UUID(request.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Fetch session
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Verify PIN
    if verify_pin(request.pin):
        session.is_owner = True
        db.commit()
        db.refresh(session)

        return PinResponse(
            is_owner=True,
            message="Welcome back, Lenoir! Your personal memories are now accessible."
        )
    else:
        return PinResponse(
            is_owner=False,
            message="I don't recognize that PIN. Let me continue as a regular assistant."
        )
