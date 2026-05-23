'use client'

import { useState, useEffect } from 'react'
import ChatWindow from './components/ChatWindow'
import AuthScreen from './components/AuthScreen'

interface AuthState {
  token: string | null
  isOwner: boolean
  authenticated: boolean
}

export default function Home() {
  const [authState, setAuthState] = useState<AuthState>({
    token: null,
    isOwner: false,
    authenticated: false,
  })

  // On mount, restore auth token from sessionStorage if it exists
  useEffect(() => {
    const stored = sessionStorage.getItem('auth_token')
    if (stored) {
      setAuthState({
        token: stored,
        isOwner: true,
        authenticated: true,
      })
    } else {
      // No stored token, mark as ready for auth (show AuthScreen)
      setAuthState((prev) => ({ ...prev, authenticated: false }))
    }
  }, [])

  // Handle auth success from AuthScreen
  const handleAuth = (token: string | null, isOwner: boolean) => {
    setAuthState({
      token,
      isOwner,
      authenticated: true,
    })
  }

  // Handle logout from ChatWindow - return to auth screen
  const handleLogout = () => {
    sessionStorage.removeItem('auth_token')
    sessionStorage.removeItem('session_id')
    setAuthState({
      token: null,
      isOwner: false,
      authenticated: false,
    })
  }

  // Show AuthScreen if not yet authenticated, otherwise show ChatWindow
  if (!authState.authenticated) {
    return (
      <main style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <AuthScreen onAuth={handleAuth} />
      </main>
    )
  }

  return (
    <main style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <ChatWindow authToken={authState.token} isOwner={authState.isOwner} onLogout={handleLogout} />
    </main>
  )
}
