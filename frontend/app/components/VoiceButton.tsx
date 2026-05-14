'use client'

import { useState, useRef } from 'react'
import styles from './VoiceButton.module.css'

interface VoiceButtonProps {
  onRecordingComplete: (audioBlob: Blob) => void
  disabled?: boolean
}

export default function VoiceButton({
  onRecordingComplete,
  disabled = false,
}: VoiceButtonProps) {
  const [isRecording, setIsRecording] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      })

      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        onRecordingComplete(audioBlob)

        // Stop audio stream
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.start()
      mediaRecorderRef.current = mediaRecorder
      setIsRecording(true)
    } catch (error) {
      console.error('Microphone access denied:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleMouseDown = () => {
    startRecording()
  }

  const handleMouseUp = () => {
    stopRecording()
  }

  return (
    <button
      className={`${styles.button} ${isRecording ? styles.recording : ''}`}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchStart={handleMouseDown}
      onTouchEnd={handleMouseUp}
      disabled={disabled}
      title="Hold to record voice"
    >
      <span className={styles.icon}>{isRecording ? '🔴' : '🎤'}</span>
      <span className={styles.text}>{isRecording ? 'Recording...' : 'Hold to speak'}</span>
    </button>
  )
}
