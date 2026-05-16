'use client'

import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import LanguageSelector from './LanguageSelector'
import { sendMessage } from '@/lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    { id: '0', role: 'assistant', content: 'Hello! How can I help you today?', timestamp: new Date() },
  ])
  const [input, setInput] = useState('')
  const [language, setLanguage] = useState('en')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input
    setInput('')
    setLoading(true)

    try {
      const userMsg: Message = { id: Date.now().toString(), role: 'user', content: userMessage, timestamp: new Date() }
      setMessages((prev) => [...prev, userMsg])

      const history = messages.map((msg) => ({ role: msg.role, content: msg.content }))
      const response = await sendMessage(userMessage, language, history)

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
        <h1 style={{ fontSize: '1.5em', margin: 0 }}>Lenoir Chatbot</h1>
        <LanguageSelector currentLanguage={language} onLanguageChange={setLanguage} />
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column' }}>
        {messages.map((msg) => (
          <MessageBubble key={msg.id} role={msg.role} content={msg.content} timestamp={msg.timestamp} />
        ))}
        {loading && <div style={{ textAlign: 'center', color: '#999' }}>Thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ padding: '16px', borderTop: '1px solid #ddd' }}>
        <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            disabled={loading}
            style={{ flex: 1, padding: '12px', border: '1px solid #ddd', borderRadius: '6px' }}
            autoFocus
          />
          <button type="submit" disabled={!input.trim() || loading} style={{ padding: '12px 24px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
