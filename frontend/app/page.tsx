'use client'

import { useState, useEffect } from 'react'
import IdentityPrompt from './components/IdentityPrompt'
import ChatWindow from './components/ChatWindow'
import { healthCheck } from '@/lib/api'

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isOwner, setIsOwner] = useState(false)
  const [isReady, setIsReady] = useState(false)

  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await healthCheck()
        if (health) {
          setIsReady(true)
        } else {
          console.warn('Backend health check failed')
          setIsReady(false)
        }
      } catch (error) {
        console.error('Backend connection error:', error)
        setIsReady(false)
      }
    }

    checkHealth()
  }, [])

  const handleIdentified = (id: string, owner: boolean) => {
    setSessionId(id)
    setIsOwner(owner)
  }

  const handleLogout = () => {
    setSessionId(null)
    setIsOwner(false)
  }

  if (!isReady) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        fontSize: '18px',
      }}>
        <div style={{
          textAlign: 'center',
          padding: '40px',
        }}>
          <h1>Connecting to backend...</h1>
          <p>Make sure your backend is running on {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</p>
        </div>
      </div>
    )
  }

  return (
    <>
      {!sessionId ? (
        <IdentityPrompt onIdentified={handleIdentified} />
      ) : (
        <ChatWindow sessionId={sessionId} isOwner={isOwner} onLogout={handleLogout} />
      )}
    </>
  )
}
