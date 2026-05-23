'use client'

/**
 * VoiceButton Component - Microphone Audio Recording
 *
 * This component provides a button that:
 * 1. Records audio from the user's microphone
 * 2. Sends the audio blob to the backend /voice/transcribe endpoint
 * 3. Returns the transcribed text to be placed in the chat input
 *
 * Why MediaRecorder?
 * - Native browser API (no npm packages needed)
 * - Works in all modern browsers (Chrome, Firefox, Safari, Edge)
 * - Records audio in WebM format (widely supported)
 * - Simple state management with useRef for MediaRecorder instance
 *
 * Usage:
 * <VoiceButton
 *   onTranscript={(text) => setInput(text)}
 *   disabled={loading}
 * />
 *
 * Accessibility:
 * - Shows clear visual feedback (mic icon when idle, stop icon when recording)
 * - Disabled when chat is loading
 * - Error messages shown if microphone access is denied
 */

import { useRef, useState } from 'react'
import { transcribeAudio } from '@/lib/api'

interface VoiceButtonProps {
  onTranscript: (text: string) => void
  disabled: boolean
}

export default function VoiceButton({ onTranscript, disabled }: VoiceButtonProps) {
  const [recording, setRecording] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const handleStartRecording = async () => {
    try {
      setError(null)

      // Request microphone access from user
      // This will trigger a browser permission prompt
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      // Create MediaRecorder with the audio stream
      // WebM format is widely supported and gives good quality with small file size
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      })

      audioChunksRef.current = []

      // Collect audio data chunks as they're recorded
      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      // When recording stops, send the audio to be transcribed
      mediaRecorder.onstop = async () => {
        // Combine all audio chunks into a single blob
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })

        try {
          // Send to backend /voice/transcribe endpoint
          const result = await transcribeAudio(audioBlob)
          // Call the callback with transcribed text (parent inserts into input)
          onTranscript(result.text)
        } catch (err) {
          setError(`Transcription failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
          console.error('Transcription error:', err)
        }

        // Stop all audio tracks to release microphone
        stream.getTracks().forEach((track) => track.stop())
      }

      // Start recording
      mediaRecorder.start()
      mediaRecorderRef.current = mediaRecorder
      setRecording(true)
    } catch (err) {
      // Common errors:
      // - NotAllowedError: User denied microphone permission
      // - NotFoundError: No microphone available
      // - NotSupportedError: Browser doesn't support getUserMedia
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          setError('Microphone permission denied. Please enable it in browser settings.')
        } else if (err.name === 'NotFoundError') {
          setError('No microphone found. Please connect a microphone.')
        } else {
          setError(`Microphone error: ${err.message}`)
        }
      } else {
        setError('Microphone error: Unknown error')
      }
      console.error('Microphone error:', err)
    }
  }

  const handleStopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop()
      setRecording(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <button
        type="button"
        onClick={recording ? handleStopRecording : handleStartRecording}
        disabled={disabled}
        style={{
          padding: '12px 24px',
          backgroundColor: recording ? '#dc3545' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          fontSize: '16px',
          fontWeight: '500',
          cursor: disabled ? 'not-allowed' : 'pointer',
          opacity: disabled ? 0.6 : 1,
          transition: 'background-color 0.2s',
        }}
        onMouseEnter={(e) => {
          if (!disabled) {
            e.currentTarget.style.backgroundColor = recording ? '#c82333' : '#0056b3'
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = recording ? '#dc3545' : '#007bff'
        }}
        title={recording ? 'Stop recording' : 'Start recording'}
      >
        {recording ? '⏹️ Stop Recording' : '🎤 Record'}
      </button>

      {error && (
        <p style={{ color: '#dc3545', fontSize: '14px', margin: 0 }}>
          {error}
        </p>
      )}
    </div>
  )
}
