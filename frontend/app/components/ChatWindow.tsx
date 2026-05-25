'use client'

import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import VoiceButton from './VoiceButton'
import { sendMessage, getChatHistory } from '@/lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ChatWindowProps {
  authToken: string | null
  isOwner: boolean
  onLogout: () => void
}

export default function ChatWindow({ authToken, isOwner, onLogout }: ChatWindowProps) {
  const welcomeMessage = isOwner
    ? "Welcome back! I'm Lenoir's secret assistant. How can I help you today?"
    : "Welcome! I'm Lenoir's assistant. (Anonymous mode) How can I help you?"

  const [messages, setMessages] = useState<Message[]>([
    { id: '0', role: 'assistant', content: welcomeMessage, timestamp: new Date() },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const language = 'en' // LLM automatically detects user language

  // Restore session_id and chat history from database on mount (v4: persistent conversations)
  useEffect(() => {
    const storedSessionId = sessionStorage.getItem('session_id')
    const storedToken = sessionStorage.getItem('auth_token')

    console.log('[ChatWindow] Mount: session_id =', storedSessionId)
    console.log('[ChatWindow] Mount: auth_token =', !!storedToken)

    if (storedSessionId) {
      console.log('[ChatWindow] Restoring session:', storedSessionId)
      setSessionId(storedSessionId)

      // Fetch chat history from backend (v4: retrieve from PostgreSQL)
      getChatHistory(storedSessionId, storedToken)
        .then((history) => {
          console.log('[ChatWindow] Got chat history:', history.length, 'messages')
          if (history.length > 0) {
            // Convert API messages to component Message format
            const restoredMessages = history.map((msg, index) => ({
              id: `${index}`,
              role: msg.role as 'user' | 'assistant',
              content: msg.content,
              timestamp: new Date(),
            }))
            // Replace initial greeting with actual history
            setMessages(restoredMessages)
            console.log('[ChatWindow] Messages restored:', restoredMessages.length)
          }
        })
        .catch((error) => {
          console.error('[ChatWindow] Failed to fetch chat history:', error)
          // If fetch fails, keep the initial greeting
        })
    } else {
      console.log('[ChatWindow] No session_id in storage, showing welcome message')
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleClear = () => {
    setMessages([
      { id: '0', role: 'assistant', content: welcomeMessage, timestamp: new Date() },
    ])
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input
    setInput('')
    setLoading(true)

    try {
      const userMsg: Message = { id: Date.now().toString(), role: 'user', content: userMessage, timestamp: new Date() }
      setMessages((prev) => [...prev, userMsg])

      // v4: Backend will fetch history from database, so we pass empty array
      const history = messages.map((msg) => ({ role: msg.role, content: msg.content }))
      const response = await sendMessage(userMessage, language, history, authToken, sessionId)

      // v4: Store session_id from response in sessionStorage for persistence
      if (response.session_id) {
        sessionStorage.setItem('session_id', response.session_id)
        setSessionId(response.session_id)
      }

      const assistantMsg: Message = { id: (Date.now() + 1).toString(), role: 'assistant', content: response.content, timestamp: new Date() }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (error) {
      console.error('Chat error:', error)
      setMessages((prev) => [...prev, { id: (Date.now() + 1).toString(), role: 'assistant', content: 'Sorry, I encountered an error.', timestamp: new Date() }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: 'white' }}>
      <div style={{ padding: '16px', borderBottom: '1px solid #ddd', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <h1 style={{ fontSize: '1.5em', margin: 0 }}>Lenoir Assistant</h1>
          <span
            style={{
              padding: '4px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 'bold',
              backgroundColor: isOwner ? '#d4edda' : '#e2e3e5',
              color: isOwner ? '#155724' : '#383d41',
            }}
          >
            {isOwner ? '🔐 Owner Mode' : '👤 Guest Mode'}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={handleClear}
            disabled={loading}
            title="Clear conversation and start fresh"
            style={{
              padding: '6px 12px',
              backgroundColor: '#ffc107',
              color: '#333',
              border: 'none',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1,
              transition: 'background-color 0.2s',
            }}
            onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = '#ffb300')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffc107')}
          >
            🗑️ Clear
          </button>

          <button
            onClick={onLogout}
            disabled={loading}
            title="Logout and return to login screen"
            style={{
              padding: '6px 12px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1,
              transition: 'background-color 0.2s',
            }}
            onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = '#c82333')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#dc3545')}
          >
            🚪 Logout
          </button>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column' }}>
        {messages.map((msg) => (
          <MessageBubble key={msg.id} role={msg.role} content={msg.content} timestamp={msg.timestamp} language={language} />
        ))}
        {loading && <div style={{ textAlign: 'center', color: '#999' }}>Thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ padding: '16px', borderTop: '1px solid #ddd' }}>
        <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            disabled={loading}
            style={{ flex: 1, padding: '12px', border: '1px solid #ddd', borderRadius: '6px' }}
            autoFocus
          />
          <VoiceButton onTranscript={setInput} disabled={loading} />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            style={{
              padding: '12px 24px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '16px',
              fontWeight: '500',
              cursor: !input.trim() || loading ? 'not-allowed' : 'pointer',
              opacity: !input.trim() || loading ? 0.6 : 1,
              transition: 'background-color 0.2s',
            }}
            onMouseEnter={(e) => {
              if (input.trim() && !loading) {
                e.currentTarget.style.backgroundColor = '#0056b3'
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#007bff'
            }}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
