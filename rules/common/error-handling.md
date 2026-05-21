# Error Handling Standards

## API Error Response Format

### Backend (FastAPI)
```python
from fastapi import HTTPException

# Standard error response
raise HTTPException(
    status_code=400,
    detail="Descriptive error message"
)

# Response body (automatic):
{
  "detail": "Descriptive error message"
}
```

### Status Code Usage

- **400**: Invalid request (validation error, missing fields)
- **401**: Authentication error (invalid token)
- **403**: Authorization error (no permission)
- **404**: Not found (resource doesn't exist)
- **422**: Pydantic validation error (malformed data)
- **500**: Server error (unhandled exception)

## Frontend Error Handling

```typescript
// lib/api.ts
export async function sendMessage(...): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_URL}/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, language, history }),
    })

    if (!response.ok) {
      // Network or API error
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(`API error: ${error.detail || response.statusText}`)
    }

    return response.json()
  } catch (error) {
    console.error('Chat error:', error)
    throw error  // Let caller handle
  }
}

// In components
const handleSendMessage = async (e: React.FormEvent) => {
  try {
    const response = await sendMessage(message, language, history, token)
    setMessages(prev => [...prev, assistantMessage])
  } catch (error) {
    // User-facing error message
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.'
    }])
    console.error(error)
  }
}
```

## Logging Standards

- **Console.error()**: Unrecoverable errors, API failures
- **Console.warn()**: Degraded functionality, warnings
- **Console.log()**: Important state changes (avoid in production)
- **Never log**: API keys, tokens, passwords, sensitive data

## Error Messages

**Good**:
- "Session not found. Please create a new session."
- "Invalid PIN. Please check and try again."
- "Failed to transcribe audio. Please try again or type manually."

**Avoid**:
- "Error 500"
- "Validation error"
- "Database connection failed"
- "Unknown error"

## Testing Error Cases

```python
# tests/test_chat.py
def test_chat_missing_message():
    response = client.post(
        "/chat/message",
        json={"language": "en"}  # Missing message
    )
    assert response.status_code == 422

def test_chat_invalid_language():
    response = client.post(
        "/chat/message",
        json={"message": "Hi", "language": "xyz"}
    )
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"].lower()
```
