import axios, { AxiosInstance } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============= Auth =============

export const identifyUser = async (message: string, sessionId?: string) => {
  const response = await api.post('/auth/identify', {
    message,
    session_id: sessionId,
  })
  return response.data
}

export const verifyPin = async (sessionId: string, pin: string) => {
  const response = await api.post('/auth/verify-pin', {
    session_id: sessionId,
    pin,
  })
  return response.data
}

// ============= Chat =============

export const streamChat = async (
  sessionId: string,
  message: string,
  language: string = 'en'
): Promise<EventSource> => {
  // Return EventSource for SSE streaming
  const url = new URL(`${API_URL}/chat/message`)
  const params = new URLSearchParams({
    session_id: sessionId,
    message,
    language,
  })

  return new EventSource(`${url}?${params.toString()}`)
}

export const chatMessage = async (
  sessionId: string,
  message: string,
  language: string = 'en'
) => {
  const response = await api.post('/chat/message', {
    session_id: sessionId,
    message,
    language,
  })
  return response.data
}

// ============= Voice =============

export const transcribeAudio = async (
  audioBlob: Blob,
  sessionId: string,
  language: string = 'en'
) => {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'audio.webm')
  formData.append('session_id', sessionId)
  formData.append('language', language)

  const response = await api.post('/voice/transcribe', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const synthesizeVoice = async (
  text: string,
  sessionId: string,
  language: string = 'en'
): Promise<Blob> => {
  const response = await api.post(
    '/voice/speak',
    {
      session_id: sessionId,
      text,
      language,
    },
    {
      responseType: 'blob',
    }
  )
  return response.data
}

// ============= Memory =============

export const addPersonalFact = async (
  sessionId: string,
  category: string,
  content: string
) => {
  const formData = new FormData()
  formData.append('session_id', sessionId)
  formData.append('category', category)
  formData.append('content', content)

  const response = await api.post('/memory/facts', formData)
  return response.data
}

export const uploadDocument = async (
  sessionId: string,
  file: File,
  description: string = ''
) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('session_id', sessionId)
  formData.append('description', description)

  const response = await api.post('/memory/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const getPersonalFacts = async (sessionId: string) => {
  const response = await api.get('/memory/facts', {
    params: {
      session_id: sessionId,
    },
  })
  return response.data
}

// ============= Health =============

export const healthCheck = async () => {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    return null
  }
}
