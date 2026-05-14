from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid
import io

from db import get_db, Session as SessionModel
from services import transcribe_audio, synthesize_speech

router = APIRouter(prefix="/voice", tags=["voice"])


class TranscribeResponse(BaseModel):
    """Response from speech-to-text."""
    transcript: str
    language: str


class SynthesizeRequest(BaseModel):
    """Request for text-to-speech."""
    session_id: str
    text: str
    language: str = "en"


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    audio: UploadFile = File(...),
    session_id: str = Form(...),
    language: str = Form(default="en"),
    db: Session = Depends(get_db)
):
    """
    Transcribe audio to text using OpenAI Whisper API.
    Expects .webm audio blob from browser MediaRecorder.
    """
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Verify session exists
    session = db.query(SessionModel).filter(SessionModel.id == session_uuid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Read audio file
        audio_data = await audio.read()

        # Transcribe using Whisper
        transcript = await transcribe_audio(audio_data, language=language)

        return TranscribeResponse(
            transcript=transcript,
            language=language
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/speak")
async def speak(request: SynthesizeRequest, db: Session = Depends(get_db)):
    """
    Convert text to speech using OpenAI TTS API.
    Returns audio stream (MP3 format).
    """
    try:
        session_uuid = uuid.UUID(request.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Verify session exists
    session = db.query(SessionModel).filter(SessionModel.id == session_uuid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Synthesize speech
        audio_bytes = await synthesize_speech(request.text, language=request.language)

        # Return as audio stream
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=response.mp3"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")
