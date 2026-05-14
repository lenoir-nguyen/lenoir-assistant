from openai import AsyncOpenAI
from config import get_settings
import io

settings = get_settings()

# Initialize async OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def transcribe_audio(audio_data: bytes, language: str = "en") -> str:
    """
    Transcribe audio to text using OpenAI Whisper API.

    Args:
        audio_data: Raw audio bytes (.webm format)
        language: Language code ('en', 'fr', 'vi')

    Returns:
        Transcribed text
    """
    # Create a file-like object from bytes
    audio_file = io.BytesIO(audio_data)
    audio_file.name = "audio.webm"

    # Call Whisper API with language hint for improved accuracy
    transcript = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language=language,
        response_format="text"
    )

    return transcript


async def synthesize_speech(text: str, language: str = "en") -> bytes:
    """
    Convert text to speech using OpenAI TTS API.

    Args:
        text: Text to synthesize
        language: Language code (used in system prompt, not API)

    Returns:
        Audio bytes in MP3 format
    """
    response = await client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
        response_format="mp3"
    )

    # Read audio bytes from response
    return response.content


async def embed_text(text: str) -> list[float]:
    """
    Generate embeddings for text using OpenAI embeddings API.

    Args:
        text: Text to embed

    Returns:
        Embedding vector (1536 dimensions)
    """
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        dimensions=1536
    )

    # Return first (and only) embedding
    return response.data[0].embedding
