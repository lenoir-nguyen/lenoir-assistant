"""
Tests for voice endpoints (Whisper STT and TTS).

These tests verify that:
1. Transcription correctly receives audio and returns transcribed text
2. TTS correctly receives text and returns audio stream
3. Missing inputs are rejected with proper HTTP error codes
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from io import BytesIO


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    from main import app
    return TestClient(app)


class TestTranscribeEndpoint:
    """Tests for POST /voice/transcribe endpoint."""

    def test_transcribe_success(self, client):
        """
        Test successful transcription.

        When a valid audio file is uploaded:
        - OpenAI Whisper is called with the audio
        - Returns { "text": "transcribed text" }
        """
        # Mock audio file content (in real test, this would be WAV/MP3/WebM)
        mock_audio = BytesIO(b"fake audio data")

        # Mock OpenAI transcription API
        with patch("routers.voice.settings") as mock_settings, \
             patch("routers.voice.client.audio.transcriptions.create") as mock_transcribe:

            mock_settings.openai_api_key = "test-key"
            mock_transcribe.return_value = MagicMock(text="Hello, how are you?")

            # Call endpoint with uploaded file
            response = client.post(
                "/voice/transcribe",
                files={"audio": ("test.wav", mock_audio, "audio/wav")}
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "text" in data
            assert data["text"] == "Hello, how are you?"

            # Verify OpenAI was called with model="whisper-1"
            mock_transcribe.assert_called_once()
            call_kwargs = mock_transcribe.call_args[1]
            assert call_kwargs["model"] == "whisper-1"

    def test_transcribe_missing_file(self, client):
        """
        Test missing audio file.

        When no file is uploaded:
        - Returns 422 Unprocessable Entity (FastAPI validation error)
        """
        response = client.post("/voice/transcribe")
        assert response.status_code == 422
        # FastAPI's validation error includes detail about missing field

    def test_transcribe_empty_audio(self, client):
        """
        Test empty audio file.

        When an empty file is uploaded:
        - OpenAI rejects it or returns error
        - We should handle gracefully
        """
        mock_audio = BytesIO(b"")

        with patch("routers.voice.client.audio.transcriptions.create") as mock_transcribe:
            mock_transcribe.side_effect = Exception("Invalid audio file")

            response = client.post(
                "/voice/transcribe",
                files={"audio": ("empty.wav", mock_audio, "audio/wav")}
            )

            # Should return 400 or 422 on error
            assert response.status_code in [400, 422, 500]


class TestSpeakEndpoint:
    """Tests for POST /voice/speak endpoint."""

    def test_speak_success(self, client):
        """
        Test successful text-to-speech.

        When text and language are provided:
        - OpenAI TTS is called with model="tts-1" and voice
        - Returns audio stream (mp3)
        """
        with patch("routers.voice.settings") as mock_settings, \
             patch("routers.voice.client.audio.speech.create") as mock_speak:

            # Mock settings
            mock_settings.openai_api_key = "test-key"
            mock_settings.tts_voice = "nova"

            # Mock TTS API returning audio stream
            mock_audio_response = BytesIO(b"fake mp3 audio data")
            mock_speak.return_value = mock_audio_response

            # Call endpoint
            response = client.post(
                "/voice/speak",
                json={"text": "Hello, how are you?", "language": "en"}
            )

            # Verify response is audio stream
            assert response.status_code == 200
            assert response.headers.get("content-type") == "audio/mpeg"
            assert b"fake mp3 audio data" in response.content

            # Verify OpenAI was called correctly
            mock_speak.assert_called_once()
            call_kwargs = mock_speak.call_args[1]
            assert call_kwargs["model"] == "tts-1"
            assert call_kwargs["voice"] == "nova"
            assert call_kwargs["input"] == "Hello, how are you?"

    def test_speak_empty_text(self, client):
        """
        Test missing or empty text.

        When text is empty or missing:
        - Returns 422 Unprocessable Entity
        """
        response = client.post(
            "/voice/speak",
            json={"text": "", "language": "en"}
        )
        assert response.status_code == 422

    def test_speak_missing_fields(self, client):
        """
        Test missing required fields.

        When text or language is missing:
        - Returns 422 Unprocessable Entity (validation error)
        """
        response = client.post("/voice/speak", json={"text": "Hello"})
        assert response.status_code == 422

        response = client.post("/voice/speak", json={"language": "en"})
        assert response.status_code == 422

    def test_speak_invalid_voice(self, client):
        """
        Test invalid TTS voice config.

        Even if user requests text, if settings.tts_voice is invalid:
        - OpenAI API should reject it
        - We return error response
        """
        with patch("routers.voice.settings") as mock_settings, \
             patch("routers.voice.client.audio.speech.create") as mock_speak:

            mock_settings.openai_api_key = "test-key"
            mock_settings.tts_voice = "invalid-voice"
            mock_speak.side_effect = Exception("Invalid voice parameter")

            response = client.post(
                "/voice/speak",
                json={"text": "Hello", "language": "en"}
            )

            # Should return error (500 or 400 depending on error handling)
            assert response.status_code in [400, 500]


class TestVoiceEndpointIntegration:
    """Integration tests for full voice workflow."""

    def test_transcribe_then_speak_workflow(self, client):
        """
        Test a complete voice workflow: transcribe → speak.

        Simulates:
        1. User records audio
        2. Audio is transcribed to text
        3. Text is sent to chat (already tested in test_chat.py)
        4. Response is converted to speech
        """
        with patch("routers.voice.settings") as mock_settings, \
             patch("routers.voice.client.audio.transcriptions.create") as mock_transcribe, \
             patch("routers.voice.client.audio.speech.create") as mock_speak:

            mock_settings.openai_api_key = "test-key"
            mock_settings.tts_voice = "nova"

            # Step 1: Transcribe
            mock_transcribe.return_value = MagicMock(text="What is the weather?")
            mock_audio_file = BytesIO(b"user audio")

            transcribe_response = client.post(
                "/voice/transcribe",
                files={"audio": ("input.wav", mock_audio_file, "audio/wav")}
            )
            assert transcribe_response.status_code == 200
            assert transcribe_response.json()["text"] == "What is the weather?"

            # Step 2: Chat (would go through /chat/message, not tested here)
            # Response would be: "The weather is sunny"

            # Step 3: Speak
            mock_speak.return_value = BytesIO(b"audio response")
            speak_response = client.post(
                "/voice/speak",
                json={"text": "The weather is sunny", "language": "en"}
            )
            assert speak_response.status_code == 200
            assert response.headers.get("content-type") == "audio/mpeg"
