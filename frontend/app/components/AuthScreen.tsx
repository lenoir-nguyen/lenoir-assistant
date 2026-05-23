'use client'

/**
 * AuthScreen Component — Owner Login & Guest Access
 *
 * Two-step authentication:
 * 1. Choose: "Login as Owner" or "Continue as Guest"
 * 2. If Owner: Enter 4-digit PIN
 *
 * Design:
 * - Simplified flow: PIN-only authentication (no passphrase)
 * - Owner login returns bearer token stored in sessionStorage
 * - Guest access requires no credentials, goes straight to chat
 * - Error messages shown clearly if login fails
 */

import { useState } from 'react'
import { login } from '@/lib/api'

interface AuthScreenProps {
  onAuth: (token: string | null, isOwner: boolean) => void
}

export default function AuthScreen({ onAuth }: AuthScreenProps) {
  const [showPinForm, setShowPinForm] = useState(false)
  const [pin, setPin] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleGuestClick = () => {
    onAuth(null, false)
  }

  const handleOwnerClick = () => {
    setShowPinForm(true)
    setError(null)
    setPin('')
  }

  const handleOwnerLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      // Send PIN as passphrase (no passphrase field in new auth)
      const result = await login(pin, '')
      // Store token in sessionStorage for persistence across page refreshes
      sessionStorage.setItem('auth_token', result.token)
      onAuth(result.token, result.is_owner)
    } catch (err) {
      setError('Incorrect PIN')
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
          Lenoir Assistant
        </h1>

        {!showPinForm ? (
          <>
            <p style={{ textAlign: 'center', color: '#666', marginBottom: '30px' }}>
              Choose how you'd like to proceed
            </p>

            {/* Guest Access Button */}
            <button
              type="button"
              onClick={handleGuestClick}
              style={{
                width: '100%',
                padding: '12px 24px',
                marginBottom: '16px',
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

            {/* Owner Login Button */}
            <button
              type="button"
              onClick={handleOwnerClick}
              style={{
                width: '100%',
                padding: '12px 24px',
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '16px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#0056b3')}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#007bff')}
            >
              🔐 Login as Owner
            </button>
          </>
        ) : (
          <>
            <p style={{ textAlign: 'center', color: '#666', marginBottom: '24px' }}>
              Enter your 4-digit PIN
            </p>

            {/* PIN Entry Form */}
            <form onSubmit={handleOwnerLogin}>
              <div style={{ marginBottom: '20px' }}>
                <input
                  type="password"
                  placeholder="Enter PIN"
                  value={pin}
                  onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
                  disabled={loading}
                  maxLength={4}
                  autoFocus
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    fontSize: '16px',
                    textAlign: 'center',
                    letterSpacing: '4px',
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
                disabled={loading || pin.length !== 4}
                style={{
                  width: '100%',
                  padding: '12px 24px',
                  marginBottom: '12px',
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '16px',
                  fontWeight: '500',
                  cursor: loading || pin.length !== 4 ? 'not-allowed' : 'pointer',
                  opacity: loading || pin.length !== 4 ? 0.6 : 1,
                  transition: 'background-color 0.2s',
                }}
                onMouseEnter={(e) => {
                  if (!loading && pin.length === 4) {
                    e.currentTarget.style.backgroundColor = '#0056b3'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#007bff'
                }}
              >
                {loading ? '⏳ Verifying...' : '✓ Verify PIN'}
              </button>

              <button
                type="button"
                onClick={() => {
                  setShowPinForm(false)
                  setPin('')
                  setError(null)
                }}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '12px 24px',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '16px',
                  fontWeight: '500',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.6 : 1,
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#5a6268')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#6c757d')}
              >
                ← Back
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
