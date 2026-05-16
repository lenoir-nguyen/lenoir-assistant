interface Props {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function MessageBubble({ role, content, timestamp }: Props) {
  const isUser = role === 'user'
  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', marginBottom: '12px' }}>
      <div style={{ maxWidth: '70%', padding: '12px 16px', borderRadius: '12px', backgroundColor: isUser ? '#007bff' : '#e9ecef', color: isUser ? 'white' : '#333' }}>
        <p style={{ margin: 0 }}>{content}</p>
        <small style={{ display: 'block', marginTop: '4px', opacity: 0.7 }}>{timestamp.toLocaleTimeString()}</small>
      </div>
    </div>
  )
}
