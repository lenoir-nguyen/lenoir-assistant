interface Message {
  role: string
  content: string
}

interface ChatResponse {
  content: string
  language: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function sendMessage(
  message: string,
  language: string,
  history: Message[]
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, language, history }),
  })

  if (!response.ok) throw new Error(`API error: ${response.statusText}`)
  return response.json()
}
