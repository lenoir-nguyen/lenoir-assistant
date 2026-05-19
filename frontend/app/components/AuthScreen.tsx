'use client'

/**
 * AuthScreen Component — Owner Login & Guest Access
 *
 * Two-panel authentication screen shown before the chat:
 * 1. "Continue as Guest" button — immediate access without credentials
 * 2. "Sign in as Owner" form — passphrase + PIN entry for personalized access
 *
 * Design:
 * - Owner login uses passphrase ("i am lenoir") + 4-digit PIN
 * - Successful login returns bearer token stored in sessionStorage
 * - Guest access requires no credentials, no token needed
 * - Error messages shown clearly if login fails
 */

import { useState } from 'react'
import { login } from '@/lib/api'

interface AuthScreenProps {
  onAuth: (token: string | null, isOwner: boolean) => void
}

export default function AuthScreen({ onAuth }: AuthScreenProps) {
  const [passphrase, setPassphrase] = useState('')
  const [pin, setPin] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleGuestClick = () => {
    onAuth(null, false)
  }

  const handleOwnerLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const result = await login(passphrase, pin)
      // Store token in sessionStorage for persistence across page refreshes
      sessionStorage.setItem('auth_token', result.token)
      onAuth(result.token, result.is_owner)
    } catch (err) {
      setError('Incorrect passphrase or PIN')
      console.error('Login error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: '#f5f5f5',
        padding: '20px',
      }}
    >
      <div
        style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          padding: '40px',
          maxWidth: '400px',
          width: '100%',
        }}
      >
        <h1 style={{ fontSize: '24px', marginBottom: '10px', textAlign: 'center' }}>
          Lenoir Chatbot
        </h1>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: '30px', margin: '0 0 30px 0' }}>
          Choose how you'd like to proceed
        </p>

        {/* Guest Access Button */}
        <button
          type="button"
          onClick={handleGuestClick}
          style={{
            width: '100%',
            padding: '12px 24px',
            marginBottom: '20px',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            fontWeight: '500',
            cursor: 'pointer',
            transition: 'background-color 0.2s',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#5a6268')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#6c757d')}
        >
          👤 Continue as Guest
        </button>

        {/* Owner Login Form */}
        <form onSubmit={handleOwnerLogin}>
          <div style={{ marginBottom: '16px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: '#333',
              }}
            >
              Passphrase
            </label>
            <input
              type="password"
              placeholder="Enter passphrase"
              value={passphrase}
              onChange={(e) => setPassphrase(e.target.value)}
              disabled={loading}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box',
                opacity: loading ? 0.6 : 1,
              }}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: '#333',
              }}
            >
              PIN
            </label>
            <input
              type="password"
              placeholder="Enter 4-digit PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
              disabled={loading}
              maxLength={4}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box',
                opacity: loading ? 0.6 : 1,
              }}
            />
          </div>

          {error && (
            <div
              style={{
                backgroundColor: '#f8d7da',
                color: '#721c24',
                padding: '12px',
                borderRadius: '6px',
                marginBottom: '16px',
                fontSize: '14px',
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !passphrase || !pin}
            style={{
              width: '100%',
              padding: '12px 24px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '16px',
              fontWeight: '500',
              cursor: loading || !passphrase || !pin ? 'not-allowed' : 'pointer',
              opacity: loading || !passphrase || !pin ? 0.6 : 1,
              transition: 'background-color 0.2s',
            }}
            onMouseEnter={(e) => {
              if (!loading && passphrase && pin) {
                e.currentTarget.style.backgroundColor = '#0056b3'
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#007bff'
            }}
          >
            {loading ? '⏳ Signing in...' : '🔐 Sign in as Owner'}
          </button>
        </form>
      </div>
    </div>
  )
}
