'use client'

/**
 * MessageBubble Component - Individual Chat Message Display
 *
 * Displays a single message in the chat with:
 * - User messages aligned to the right, assistant to the left
 * - Timestamp for each message
 * - Speaker button on assistant messages (v2 voice feature)
 *
 * Why separate component?
 * - Reusable for both user and assistant messages
 * - Keeps MessageBubble logic clean
 * - Easy to enhance (e.g., add copy button, reactions later)
 */

import { useState } from 'react'
import { speakText } from '@/lib/api'

interface Props {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  language?: string // For TTS voice selection
}

export default function MessageBubble({ role, content, timestamp, language = 'en' }: Props) {
  const isUser = role === 'user'
  const [speaking, setSpeaking] = useState(false)
  const [error, setError] = useState<string | null>(null)

  /**
   * Handle speaker button click - convert message to speech and play it.
   *
   * Why only on assistant messages?
   * - Only assistant responses benefit from audio playback
   * - User is unlikely to want to hear their own message back
   * - Reduces visual clutter
   */
  const handleSpeak = async () => {
    try {
      setError(null)
      setSpeaking(true)

      // Get audio blob from backend TTS endpoint
      const audioBlob = await speakText(content, language)

      // Create playable audio element and play it
      const audio = new Audio(URL.createObjectURL(audioBlob))
      audio.play()

      // Clean up blob URL when audio finishes
      audio.onended = () => {
        URL.revokeObjectURL(audio.src)
      }
    } catch (err) {
      setError(`TTS failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
      console.error('TTS error:', err)
    } finally {
      setSpeaking(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', marginBottom: '12px' }}>
      <div style={{ maxWidth: '70%', padding: '12px 16px', borderRadius: '12px', backgroundColor: isUser ? '#007bff' : '#e9ecef', color: isUser ? 'white' : '#333' }}>
        <p style={{ margin: 0 }}>{content}</p>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px', gap: '8px' }}>
          <small style={{ opacity: 0.7 }}>{timestamp.toLocaleTimeString()}</small>

          {/* Speaker button - only show on assistant messages */}
          {!isUser && (
            <button
              onClick={handleSpeak}
              disabled={speaking}
              style={{
                background: 'none',
                border: 'none',
                cursor: speaking ? 'not-allowed' : 'pointer',
                fontSize: '1em',
                opacity: speaking ? 0.5 : 0.7,
              }}
              title="Hear this message"
            >
              {speaking ? '⏳' : '🔊'}
            </button>
          )}
        </div>

        {/* Show error if TTS failed */}
        {error && <small style={{ display: 'block', color: isUser ? '#ffcccc' : '#cc0000', marginTop: '4px' }}>{error}</small>}
      </div>
    </div>
  )
}
