"""
Voice router for speech-to-text (Whisper) and text-to-speech (TTS).

This module implements the voice API with support for:
- Audio transcription using OpenAI Whisper model
- Text-to-speech synthesis using OpenAI TTS API
- Multi-language support for TTS output
- Streaming audio responses

Why these endpoints exist:
- Whisper STT: Converts user audio input to text (v2 voice feature)
- TTS: Converts chat responses to audio (v2 voice feature)
- OpenAI was chosen because we're already using OpenAI for chat,
  so same API key covers all three features (chat, transcription, TTS)

Design notes:
- Transcription and TTS are separate endpoints (DRY principle)
  because they serve different purposes in the UI
- Transcription returns JSON (easy to insert into text input)
- TTS returns audio stream (easy to play in browser)
- Both are stateless and can be called independently
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from openai import OpenAI
from config import get_settings
import io

router = APIRouter(prefix="/voice", tags=["voice"])
settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ============================================================================
# Data Models
# ============================================================================


class TranscribeResponse(BaseModel):
    """Response from speech-to-text endpoint."""
    text: str = Field(..., description="Transcribed text from audio file")


class SpeakRequest(BaseModel):
    """Request for text-to-speech endpoint."""
    text: str = Field(..., min_length=1, description="Text to convert to speech")
    language: str = Field(default="en", description="Language code (en, fr, vi)")


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Convert speech audio to text using OpenAI Whisper.

    **Purpose:** v2 feature - allows users to input messages by voice

    **How it works:**
    1. Receives audio file (webm, mp4, wav, etc.)
    2. Sends to OpenAI Whisper model for transcription
    3. Returns transcribed text
    4. Frontend inserts text into input field for user to see/edit before sending

    **Why Whisper?**
    - Highest accuracy for multiple languages (en, fr, vi)
    - Fast (~1-3 seconds for typical message)
    - Included in same OpenAI API (same OPENAI_API_KEY)
    - No additional credentials needed

    **Args:**
        audio (UploadFile): Audio file from browser MediaRecorder
                          Supported formats: webm, mp4, wav, flac, aac, ogg

    **Returns:**
        TranscribeResponse: { "text": "transcribed message" }

    **Raises:**
        HTTPException: 422 if no file provided
                      400 if file is invalid or unsupported
                      500 if OpenAI API fails

    **Example (frontend):**
        const formData = new FormData()
        formData.append('audio', audioBlob)
        const response = await fetch('/voice/transcribe', {
            method: 'POST',
            body: formData
        })
        const { text } = await response.json()
    """
    if not audio:
        raise HTTPException(status_code=422, detail="Audio file required")

    try:
        # Read audio file from upload
        audio_data = await audio.read()

        # Call OpenAI Whisper to transcribe
        # model="whisper-1" is the only Whisper model available (as of 2026)
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=(audio.filename, io.BytesIO(audio_data), audio.content_type),
            language=None  # Auto-detect language from audio
        )

        return TranscribeResponse(text=transcription.text)

    except Exception as e:
        # Log error for debugging
        print(f"Transcription error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to transcribe audio: {str(e)}"
        )


@router.post("/speak")
async def speak_text(request: SpeakRequest):
    """
    Convert text to speech using OpenAI TTS.

    **Purpose:** v2 feature - allows users to hear responses as audio

    **How it works:**
    1. Receives text and language
    2. Sends to OpenAI TTS for voice synthesis
    3. Returns audio stream (mp3)
    4. Frontend plays audio via HTML5 audio element

    **Why TTS?**
    - Natural-sounding voices (model="tts-1" is fast and good quality)
    - Includes 6 voice options (alloy, echo, fable, onyx, nova, shimmer)
    - Same OpenAI API - no new credentials needed
    - Streaming response keeps latency low

    **Args:**
        request (SpeakRequest): JSON body with text and language
            - text: str (required, non-empty) — the message to speak
            - language: str (default="en") — language code (en, fr, vi)

    **Returns:**
        StreamingResponse: mp3 audio stream (content-type: audio/mpeg)
        Can be directly passed to HTML5 <audio> element or Audio() constructor

    **Raises:**
        HTTPException: 422 if text is empty
                      422 if required fields missing
                      500 if OpenAI API fails

    **Example (frontend):**
        const response = await fetch('/voice/speak', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: 'The weather is sunny',
                language: 'en'
            })
        })
        const audioBlob = await response.blob()
        const audio = new Audio(URL.createObjectURL(audioBlob))
        audio.play()
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=422, detail="Text cannot be empty")

    try:
        # Call OpenAI TTS
        # model="tts-1" = fast, good quality (vs "tts-1-hd" = highest quality but slower)
        # voice = settings.tts_voice (default "nova", configurable)
        # Why streaming? Allows browser to start playing audio before full response received
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice=settings.tts_voice,
            input=request.text
        )

        # Wrap the audio stream in a StreamingResponse
        # This allows the browser to receive audio as it's generated
        # and start playing it before the full audio is ready
        return StreamingResponse(
            io.BytesIO(speech_response.content),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline"}
        )

    except Exception as e:
        # Log error for debugging
        print(f"TTS error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )
