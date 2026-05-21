---
name: environment-secrets-management
description: Patterns for managing secrets, API keys, and environment variables safely across dev/prod
origin: lenoir-assistant v1.0.0
---

# Environment Secrets Management

## Overview

Keeping API keys, database credentials, and other secrets secure while maintaining developer productivity is critical. This skill captures the three-tier pattern used in Lenoir Assistant.

## Pattern: Three-Tier Secret Storage

### Tier 1: Project Local (Development)

**Files**: `.env` (git-ignored), `.env.local.example` (committed)

**Purpose**: Developer's local machine secrets for testing

**Contents** (.env.example):
```bash
# Backend
OPENAI_API_KEY=sk-proj-your-key-here
DATABASE_URL=postgresql://localhost/lenoir_assistant
REDIS_URL=redis://localhost:6379
OWNER_PIN_HASH=$2b$12$...bcrypt-hash...

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**How It Works**:
```bash
# Developer copies example
cp .env.example .env
# Edit .env with their own keys
# .env is git-ignored, never committed
```

**Security**: 
- ✅ Keys only on developer's machine
- ✅ Cannot be exposed via git
- ✅ Easy onboarding (template provided)
- ✅ Different per developer if needed

### Tier 2: Production Secrets (Cloud)

**Where**: Railway dashboard (backend), Vercel dashboard (frontend)

**How to Set** (Railway example):
1. Go to Project Settings → Variables
2. Add `OPENAI_API_KEY=sk-proj-...`
3. Railway injects as environment variables at runtime
4. Never stored in git

**How to Set** (Vercel example):
1. Go to Project Settings → Environment Variables
2. Add `NEXT_PUBLIC_API_URL=https://api.lenoir.app`
3. Vercel injects during build and runtime

**Security**:
- ✅ Secrets encrypted at rest
- ✅ Access controlled via IAM
- ✅ Audit logs track access
- ✅ Different values per environment (staging, prod)

### Tier 3: Application-Level Secrets (Config)

**Files**: `config.py` (backend), `.env` loading (frontend)

**Purpose**: Load secrets into application at startup

**Backend** (Python):
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str  # Required - loaded from .env or Railway
    DATABASE_URL: str    # Required
    OWNER_PIN_HASH: str = ""  # Optional
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Usage in routers
client = OpenAI(api_key=settings.OPENAI_API_KEY)
```

**Frontend** (Next.js):
```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Security**:
- ✅ Type-safe secret access (Pydantic validation)
- ✅ Required secrets enforced at startup
- ✅ Clear error messages if missing
- ✅ Never log secrets (type hints help IDE avoid exposing them)

## Practical Workflow

### 1. Local Development
```bash
cd backend
cp .env.example .env
# Edit .env: add your OPENAI_API_KEY
python -m uvicorn main:app --reload
# .env loaded automatically
```

### 2. First Deployment to Railway
```bash
# Push code to GitHub
git push origin main

# Go to Railway > Project > Variables
# Add production values:
OPENAI_API_KEY=sk-proj-production-key
DATABASE_URL=postgresql://user:pass@db.railway.internal/lenoir
REDIS_URL=redis://redis.railway.internal:6379
OWNER_PIN_HASH=bcrypt-hash
```

### 3. Adding a New Secret
```bash
# 1. Update .env.example (template)
echo "NEW_SECRET_KEY=" >> .env.example

# 2. Update config.py (application)
class Settings(BaseSettings):
    # ... existing ...
    NEW_SECRET_KEY: str  # Required

# 3. Local developer
cp .env.example .env
# Add value to .env

# 4. Production (Railway/Vercel)
# Add to dashboard variables

# 5. Test
pytest backend/tests/  # Should pass
```

## Anti-Patterns to Avoid

❌ **Hard-coding secrets**:
```python
# Bad
OPENAI_API_KEY = "sk-proj-abc123"  # Never do this!
```

❌ **Committing .env file**:
```bash
# Bad
git add .env  # Will expose all keys
```

❌ **Logging secrets**:
```python
# Bad
print(f"Connecting with key: {settings.OPENAI_API_KEY}")
```

❌ **Passing secrets via URL**:
```python
# Bad
fetch(`/api/data?key=${apiKey}`)  # Key in URL history
```

## Checklist for New Projects

- [ ] Create `.env.example` with all required keys (empty values)
- [ ] Add `.env` to `.gitignore`
- [ ] Create `config.py` with Pydantic Settings
- [ ] Update README to explain secret setup
- [ ] Test locally with `.env` file
- [ ] Add production secrets to Railway/Vercel dashboards
- [ ] Test in production (verify secrets loaded correctly)
- [ ] Document required secrets in SETUP_GUIDE.md

---

## See Also

- `rules/common/error-handling.md` — Handling missing secrets errors
- `SETUP_GUIDE.md` — Detailed setup with example values
