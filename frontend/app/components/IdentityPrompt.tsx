'use client'

import { useState } from 'react'
import { identifyUser, verifyPin } from '@/lib/api'
import styles from './IdentityPrompt.module.css'

interface IdentityPromptProps {
  onIdentified: (sessionId: string, isOwner: boolean) => void
}

export default function IdentityPrompt({ onIdentified }: IdentityPromptProps) {
  const [stage, setStage] = useState<'greeting' | 'pin'>('greeting')
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [isOwner, setIsOwner] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('Welcome! Who are you?')

  const handleGreeting = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    setLoading(true)
    try {
      const response = await identifyUser(input)
      setSessionId(response.session_id)

      if (response.requires_pin) {
        setStage('pin')
        setMessage(response.message)
        setInput('')
      } else {
        // Stranger user
        setIsOwner(false)
        onIdentified(response.session_id, false)
      }
    } catch (error) {
      setMessage('Error identifying user. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handlePinSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    setLoading(true)
    try {
      const response = await verifyPin(sessionId, input)

      if (response.is_owner) {
        setIsOwner(true)
        onIdentified(sessionId, true)
      } else {
        setMessage(response.message)
        setInput('')
        setStage('greeting')
      }
    } catch (error) {
      setMessage('Error verifying PIN. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Lenoir Chatbot</h1>
        <p className={styles.message}>{message}</p>

        <form onSubmit={stage === 'greeting' ? handleGreeting : handlePinSubmit}>
          <input
            type={stage === 'pin' ? 'password' : 'text'}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={stage === 'greeting' ? 'Type your message...' : 'Enter PIN...'}
            disabled={loading}
            autoFocus
            className={styles.input}
          />
          <button type="submit" disabled={loading || !input.trim()} className={styles.button}>
            {loading ? 'Processing...' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  )
}
