interface Message {
  role: string
  content: string
}

interface ChatResponse {
  content: string
  language: string
}

interface TranscribeResponse {
  text: string
}

interface SpeakRequest {
  text: string
  language: string
}

interface LoginResponse {
  token: string
  is_owner: boolean
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function login(
  passphrase: string,
  pin: string
): Promise<LoginResponse> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ passphrase, pin }),
  })

  if (!response.ok) throw new Error(`Login failed: ${response.statusText}`)
  return response.json()
}

export async function sendMessage(
  message: string,
  language: string,
  history: Message[],
  authToken: string | null = null
): Promise<ChatResponse> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`
  }

  const response = await fetch(`${API_URL}/chat/message`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ message, language, history }),
  })

  if (!response.ok) throw new Error(`API error: ${response.statusText}`)
  return response.json()
}

/**
 * Convert audio blob to text using OpenAI Whisper.
 *
 * Why separate from sendMessage?
 * - Transcription is optional and only triggered when user clicks mic
 * - Allows user to see and edit transcribed text before sending
 * - Reduces API calls if user doesn't use voice feature
 *
 * @param audioBlob - Audio recording from MediaRecorder (webm format)
 * @returns Promise with transcribed text
 * @throws Error if transcription fails
 */
export async function transcribeAudio(audioBlob: Blob): Promise<TranscribeResponse> {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'audio.webm')

  const response = await fetch(`${API_URL}/voice/transcribe`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) throw new Error(`Transcription failed: ${response.statusText}`)
  return response.json()
}

/**
 * Convert text to speech using OpenAI TTS.
 *
 * Why separate from sendMessage?
 * - TTS is optional and only triggered when user clicks speaker button
 * - Allows user to hear responses on demand, not automatically
 * - Each message can be heard independently
 *
 * @param text - The message text to convert to speech
 * @param language - Language code (en, fr, vi) for proper pronunciation
 * @returns Promise with mp3 audio blob that can be played with Audio()
 * @throws Error if TTS fails
 */
export async function speakText(text: string, language: string): Promise<Blob> {
  const response = await fetch(`${API_URL}/voice/speak`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, language }),
  })

  if (!response.ok) throw new Error(`TTS failed: ${response.statusText}`)
  return response.blob()
}
