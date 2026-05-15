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
    Convert speech to text using OpenAI Whisper API.

    Flow:
    1. Browser MediaRecorder captures audio (webm format, opus codec)
    2. Frontend sends audio blob + session_id + language to this endpoint
    3. Backend passes audio to Whisper API with language hint
    4. Whisper returns transcript text
    5. Frontend displays transcript in input field

    Args:
        audio: Audio file from browser MediaRecorder (webm/opus)
        session_id: Session UUID for ownership validation
        language: Language code (en/fr/vi) passed to Whisper for accuracy
        db: Database connection for session verification

    Returns:
        TranscribeResponse with transcript text and language
    """
    # Validate session ID format
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Verify session exists in database
    session = db.query(SessionModel).filter(SessionModel.id == session_uuid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Read audio blob from request
        audio_data = await audio.read()

        # Call Whisper API with language hint for better accuracy
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

    Flow:
    1. Frontend detects assistant response in chat
    2. Sends response text + session_id + language to this endpoint
    3. Backend calls OpenAI TTS API (model: tts-1, voice: nova)
    4. Receives MP3 audio stream from OpenAI
    5. Returns audio directly to frontend <audio> element
    6. Browser plays audio automatically

    Args:
        request: SynthesizeRequest with text, session_id, language
        db: Database connection for session verification

    Returns:
        StreamingResponse with MP3 audio stream
    """
    # Validate session ID format
    try:
        session_uuid = uuid.UUID(request.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Verify session exists in database
    session = db.query(SessionModel).filter(SessionModel.id == session_uuid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Call OpenAI TTS API to generate audio from text
        # Language parameter ensures correct pronunciation
        audio_bytes = await synthesize_speech(request.text, language=request.language)

        # Return MP3 stream to frontend for playback
        # Headers set content type and disposition for inline playback
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=response.mp3"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")
