---
name: multilingual-chat
description: Patterns for building multilingual chat applications supporting multiple languages with dynamic system prompts
origin: lenoir-assistant v1.0.0
---

# Multilingual Chat Patterns

## Overview

Handling multiple languages in a chat application requires careful attention to system prompts, language selection UI, and API contracts. This skill captures proven patterns from Lenoir Assistant.

## Pattern 1: Language-Aware System Prompts

**What**: System messages that instruct the LLM to respond in the user's selected language.

**How**:
```python
# Backend: config.py or routers/chat.py
SYSTEM_PROMPT_TEMPLATE = """You are a helpful assistant.
Always respond in {language}."""

language = request.language  # "en", "fr", "vi"
system_prompt = SYSTEM_PROMPT_TEMPLATE.format(language=language)
```

**Why**:
- Explicit language instruction improves response quality
- Template separates prompt logic from language code
- One source of truth for system message

**When to Use**:
- OpenAI API calls with multi-language support
- Need consistent language across conversation
- Language can change mid-conversation

## Pattern 2: Language Selector Component

**What**: Frontend UI component for language selection with visual indicators.

**How** (React/TypeScript):
```typescript
// LanguageSelector.tsx
interface LanguageSelectorProps {
  currentLanguage: string
  onLanguageChange: (lang: string) => void
}

const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'vi', name: 'Tiếng Việt', flag: '🇻🇳' },
]

export default function LanguageSelector({ currentLanguage, onLanguageChange }: LanguageSelectorProps) {
  return (
    <div style={{ display: 'flex', gap: '8px' }}>
      {LANGUAGES.map(lang => (
        <button
          key={lang.code}
          onClick={() => onLanguageChange(lang.code)}
          style={{
            padding: '8px 12px',
            backgroundColor: currentLanguage === lang.code ? '#007bff' : '#e9ecef',
            color: currentLanguage === lang.code ? 'white' : 'black',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {lang.flag} {lang.name}
        </button>
      ))}
    </div>
  )
}
```

**Why**:
- Flags provide visual language identification
- State-based button styling shows current selection
- Easy to extend with new languages

**When to Use**:
- Multi-language applications
- Need persistent language selection
- UX benefit from clear visual indicators

## Pattern 3: API Contract for Language

**What**: Consistent request/response format that includes language.

**How**:
```typescript
// Frontend: lib/api.ts
interface ChatRequest {
  message: string
  language: string  // "en", "fr", "vi"
  history?: Array<{ role: string; content: string }>
}

interface ChatResponse {
  content: string
  language: string  // Echo back the language used
}
```

**Why**:
- API contract documents expected language codes
- Response echoes language to confirm what was used
- Frontend can validate language before sending

**When to Use**:
- RESTful APIs with language-specific responses
- Need to track language per request
- Debugging language-related issues

## Pattern 4: Language Persistence Strategy

**What**: How to keep language selection across page refreshes.

**How**:
```typescript
// Frontend: ChatWindow.tsx
const [language, setLanguage] = useState('en')

useEffect(() => {
  // Option A: sessionStorage (cleared on browser close)
  const stored = sessionStorage.getItem('language')
  if (stored) setLanguage(stored)
}, [])

const handleLanguageChange = (lang: string) => {
  setLanguage(lang)
  sessionStorage.setItem('language', lang)
  // Also send to backend to cache there (optional)
}
```

**Backend** (Redis caching):
```python
# routers/chat.py
async def get_or_create_session(session_id, language):
    cache_key = f"session:{session_id}"
    cached = await cache_get(cache_key)
    if cached:
        language = cached.get("language", language)
    else:
        await cache_set(cache_key, {"language": language}, ttl=86400)
    return language
```

**Why**:
- sessionStorage: Per-browser, cleared on close (reasonable for guest)
- Backend cache: Survives client-side clears (useful for owners, v4+)
- Avoids losing user preference during session

**When to Use**:
- Language should persist during session
- Users might refresh page mid-conversation
- Support both guest (sessionStorage) and owner (DB)

## Pattern 5: Language Validation

**What**: Ensure only supported languages are used.

**How** (Backend):
```python
# config.py
SUPPORTED_LANGUAGES = ["en", "fr", "vi"]

# routers/chat.py
from fastapi import HTTPException

@router.post("/chat/message")
async def chat_message(request: ChatRequest):
    if request.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Language '{request.language}' not supported. Choose from {SUPPORTED_LANGUAGES}"
        )
    # ... rest of endpoint
```

**Why**:
- Prevents invalid language codes from reaching OpenAI
- Provides clear error messages to frontend
- Centralized list of supported languages

**When to Use**:
- Accept language from untrusted sources (user input)
- Want explicit error handling for bad language codes
- Central configuration of supported languages

## Best Practices

1. **Centralize Language List**: Define supported languages in one place (config)
2. **Always Validate**: Check language before using in API calls
3. **Echo Language in Response**: Help client debug language mismatches
4. **Support Language Change Mid-Conversation**: Allow switching languages without clearing history
5. **Test All Languages**: Verify system prompt formatting works for all supported languages
6. **Use Standards**: Stick to ISO 639-1 two-letter codes (en, fr, vi)

## Common Pitfalls

❌ **Hard-coding language prompts**: Makes adding languages difficult
```python
# Bad
if language == "en":
    system_prompt = "..."
elif language == "fr":
    system_prompt = "..."
```

✅ **Use template with format**: Easier to maintain
```python
# Good
SYSTEM_PROMPT = "Always respond in {language}"
system_prompt = SYSTEM_PROMPT.format(language=language)
```

---

## See Also

- `rules/common/multilingual.md` — Multilingual development conventions
- `rules/common/error-handling.md` — Error response patterns
