# Reusable Skills & Patterns

This document captures patterns, best practices, and lessons learned from building the Lenoir Chatbot. These are proven approaches you can reuse in future projects.

---

## 1. Documentation Structure (6-File Pattern)

**Pattern**: Comprehensive project documentation using a consistent 6-file structure in `/docs` folder.

**Files**:
1. **VERSIONS.md** — Version history (brief entries, one per version)
2. **SETUP_GUIDE.md** — Local setup + production deployment (step-by-step)
3. **PROJECT_DETAILS.md** — Complete technical reference (architecture, files, API)
4. **IMPLEMENTATION_SUMMARY.md** — Code walkthrough + testing procedures
5. **PROMPT.md** — Original requirements (rephrased for AI regeneration)
6. **REUSABLE_SKILLS.md** — This file (patterns for future projects)

Plus: **README.md** at root with links to all /docs files.

**Why**: 
- Single source of truth for each aspect (setup, details, testing, requirements)
- Each file serves a specific audience (devs, new team members, AI assistants)
- PROMPT.md allows anyone to regenerate the project exactly
- REUSABLE_SKILLS.md creates a library of best practices

**How to Apply**:
- Create `/docs` folder in every new project
- Start with this 6-file structure as a template
- Update each file as you build each version
- Link from README.md to each /docs file

**Example for Future Project**:
```
myproject/
├── README.md
├── docs/
│   ├── VERSIONS.md
│   ├── SETUP_GUIDE.md
│   ├── PROJECT_DETAILS.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PROMPT.md
│   └── REUSABLE_SKILLS.md
├── frontend/
├── backend/
└── ...
```

---

## 2. Environment Secrets: Three-Tier Storage

**Pattern**: Keep credentials secure using three distinct storage locations.

**Tier 1: Project Local (Git-ignored)**
- Files: `.env`, `.env.local` in project root
- Contains: Development + production secrets
- Example: `OPENAI_API_KEY=sk-proj-...`
- Git: Add to `.gitignore`
- Access: Only from this machine, only you can read

**Tier 2: Examples (Committed)**
- Files: `.env.example`, `.env.local.example` in project root
- Contains: No real values, structure only
- Example: `OPENAI_API_KEY=sk-proj-your-key-here`
- Git: Committed to repo
- Access: Shows structure for new team members

**Tier 3: Global (Outside Repo)**
- Files: `~/.claude/settings.local.json` or similar per OS
- Contains: Secrets needed across multiple projects (GitHub PAT, etc.)
- Example: `{ "env": { "GITHUB_TOKEN": "ghp_..." } }`
- Git: Never in any repo
- Access: Only you can read, used for all projects

**Why**:
- Prevents accidental credential leakage to git
- Team members can see structure without accessing secrets
- Cross-project secrets (GitHub PAT) don't need duplication
- Clear separation of concerns (dev, example, global)

**How to Apply**:
1. Create `.env.example` and `.env.local.example` with zero real values
2. Add `.env` and `.env.local` to `.gitignore`
3. Store cross-project secrets in global config outside repo
4. Document this in SETUP_GUIDE.md
5. Add pre-commit hook to check for leaked secrets (future)

**Checklist**:
```
✓ .env.example committed (structure only)
✓ .env in .gitignore
✓ .env.local.example committed (structure only)
✓ .env.local in .gitignore
✓ GITHUB_TOKEN in ~/.claude/settings.local.json (global, outside repo)
✓ Instructions in SETUP_GUIDE.md on how to populate .env/.env.local
```

---

## 3. Git Workflow: Pull Before Push

**Pattern**: Always pull latest changes from remote before attempting to push.

**Workflow**:
```bash
# Before pushing any changes:
git pull origin main        # Fetch latest, merge if needed
# Resolve any conflicts if they occur
git push origin main        # Now push your changes
```

**Why**:
- Prevents non-fast-forward pushes
- Avoids needing `git push --force` (destructive)
- Ensures you have context of other changes
- Makes conflict resolution easier (smaller diffs)
- Keeps history linear and clear

**When to Use**:
- Before every `git push` (make it a habit)
- Essential in team environments
- Critical for CI/CD pipelines

**Tools to Prevent Mistakes**:
- Git hook (pre-push): Can auto-pull before push
- IDE integration: Many IDEs warn when behind remote
- Branch protection: Require pull requests (team setting)

**What NOT to Do**:
- ❌ `git push --force` (destructive, rewrites history)
- ❌ `git push --force-with-lease` (only for exceptional cases)
- ❌ Skipping pull when you know you're behind

---

## 4. Incremental Versioning: Build → Test → Deploy → Repeat

**Pattern**: Release versions incrementally, ensuring each version is production-ready before moving to next.

**Version Cycle**:
1. **Build**: Implement all features for version
2. **Test**: Local end-to-end, type checking, compilation
3. **Document**: Update `/docs/VERSIONS.md` with entry
4. **Deploy**: Push to production (Railway, Vercel, etc.)
5. **Verify**: Test live URLs, confirm working
6. **Repeat**: Move to next version

**Why**:
- Each version is independently deployable
- Bugs are isolated to specific version
- Users can stay on stable version while v2+ is in development
- Easier to debug (smaller feature set per version)
- Builds confidence: "v1 works, let's build v2"

**Example from Lenoir Chatbot**:
```
v1.0.0 (May 15)  - Basic chat              ✅ Deployed
v2.0.0 (planned) - Voice input/output      ⏳ Not started
v3.0.0 (planned) - Authentication + PIN    ⏳ Not started
v4.0.0 (planned) - LangChain + Database    ⏳ Not started
v5.0.0 (planned) - RAG + Personalization   ⏳ Not started
```

**Documentation Entry**:
```markdown
## v1.0.0 — Basic Chat SPA (2026-05-15)

**Status**: ✅ Complete & Deployed

**Features**:
- Text-based chat
- Language selection
- GPT-4o integration

**Testing**: ✅ Local end-to-end working
```

**How to Apply**:
- Plan versions upfront (in PROMPT.md and VERSIONS.md)
- Implement one version completely before starting next
- Add version entry to `docs/VERSIONS.md` when complete
- Tag git commits: `v1.0.0`, `v2.0.0`, etc.
- Consider keeping old version branches for reference

---

## 5. Monorepo Structure: /frontend, /backend, /docs

**Pattern**: Organize related services in single repository with clear folder separation.

**Structure**:
```
project-name/
├── README.md                    # Root overview
├── .gitignore                  # Global ignore rules
├── .git/                        # Single git repo
│
├── frontend/                    # Next.js/React SPA
│   ├── app/
│   ├── lib/
│   ├── package.json
│   ├── .env.local.example
│   └── .env.local (git-ignored)
│
├── backend/                     # FastAPI/Python service
│   ├── main.py
│   ├── routers/
│   ├── requirements.txt
│   ├── .env.example
│   └── .env (git-ignored)
│
└── docs/                        # Documentation (6 files)
    ├── VERSIONS.md
    ├── SETUP_GUIDE.md
    ├── PROJECT_DETAILS.md
    ├── IMPLEMENTATION_SUMMARY.md
    ├── PROMPT.md
    └── REUSABLE_SKILLS.md
```

**Why**:
- Single source of truth (one git repo)
- Easy to deploy together or separately
- Shared documentation
- Clear ownership (frontend = /frontend, backend = /backend)
- Easier for small teams or solo developers

**Deployment Options**:
- Both from main branch (auto-deploy on push)
- Different CI/CD jobs per folder (monorepo-aware)
- Separate platforms: Vercel for /frontend, Railway for /backend

**How to Apply**:
- Create `/frontend`, `/backend`, `/docs` at project root
- Git ignore rules specific to each folder
- Root `README.md` links to each folder
- Deployment scripts aware of folder structure

---

## 6. Stateless API Design: Client Sends Full Context

**Pattern**: Backend doesn't maintain session state; client sends everything needed with each request.

**Request**:
```json
{
  "message": "Hello",
  "language": "en",
  "history": [
    { "role": "user", "content": "Hi" },
    { "role": "assistant", "content": "Hello!" }
  ]
}
```

**Benefits**:
- No session database needed (v1)
- Trivial horizontal scaling (any server handles any request)
- Client can display history immediately (optimistic updates)
- No session timeout bugs
- Simpler debugging (request = complete context)

**Tradeoffs**:
- History grows with each message (eventually limit size)
- More data in each request (bandwidth)
- Can't have server-side-only decisions (all state is transparent)
- v4+ moves to database (but this pattern works for v1-v3)

**When to Use**:
- Early versions with small history
- Stateless microservices
- APIs with high concurrency requirements
- MVP/proof-of-concept work

**When NOT to Use**:
- Massive conversation histories (use database, v4+)
- Sensitive session data (use cookies + sessions, with tokens)
- Real-time collaboration (use WebSocket + server state)

**Migration Path**:
- v1-v3: Stateless (client sends history)
- v4+: Database-backed (server loads from DB, client sends limit=50)

---

## 7. Type Safety: TypeScript + Pydantic Across Stack

**Pattern**: Use type checking on both frontend and backend to catch errors early.

**Backend (Pydantic)**:
```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    language: str
    history: List[Message]

# FastAPI automatically validates incoming JSON against this schema
# If JSON doesn't match, returns 422 error immediately
```

**Frontend (TypeScript)**:
```typescript
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

// TypeScript checks all uses of Message at compile time
const messages: Message[] = []  // Type-safe array
```

**Benefits**:
- Compile-time errors caught before runtime
- IDE autocomplete and refactoring support
- Documentation embedded in types
- Fewer runtime surprises
- Easier refactoring (rename field → IDE finds all uses)

**Investment**:
- More up-front time writing type definitions
- Requires understanding of generics, unions, interfaces
- Can feel verbose initially

**How to Apply**:
- Define types for every data structure (Pydantic models + TS interfaces)
- Use strict mode: `tsconfig.json` with `"strict": true`
- Never use `any` (defeats purpose)
- Test that types match between frontend and backend

**Tooling**:
- TypeScript compiler: `tsc --noEmit` (type check without building)
- Pydantic: automatic validation + JSON schema generation
- VS Code: Excellent TypeScript support built-in

---

## 8. Auto-Deployment from GitHub: Push to Deployed

**Pattern**: Every push to main branch automatically deploys to production.

**Setup (Vercel + Railway)**:
1. Connect GitHub repo to Vercel
2. Connect GitHub repo to Railway
3. Both platforms watch main branch
4. On push: automatic build → deploy

**Workflow**:
```bash
git commit -m "v1.0.0: Basic chat"
git push origin main
# Vercel: detects push, builds frontend, deploys to vercel.app
# Railway: detects push, builds backend, deploys to railway.app
# Both within ~2-5 minutes
```

**Requirements**:
- GitHub repo is public or platforms have access
- GitHub secrets configured (SSH keys, PATs)
- Environment variables set in Vercel + Railway dashboards
- `.gitignore` includes all local artifacts (node_modules, __pycache__, .next, .env)

**Monitoring**:
- Vercel: Dashboard shows build status + logs
- Railway: Dashboard shows deployment logs
- Set up Slack/email notifications for failures

**Rollback**:
- Push a fix commit (revert or new code)
- New push auto-deploys fixed version
- If urgent: Railway supports immediate redeploy from commit history

---

## 9. CORS Best Practices: Restrict to Known Origins

**Pattern**: Allow API calls only from specific, trusted frontend URLs.

**Backend Code (FastAPI)**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://my-app.vercel.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Why**:
- Prevents unauthorized cross-origin requests
- Blocks CSRF attacks from other websites
- Restricts API to intended clients only
- Security best practice

**Pitfalls to Avoid**:
- ❌ `allow_origins=["*"]` (allows anyone to call API)
- ❌ `allow_origins=["*"]` + `allow_credentials=True` (browser rejects anyway)
- ❌ Hardcoding production URL only (breaks local development)

**How to Apply**:
- Use environment variable for allowed origins: `FRONTEND_URL`
- Development: localhost:3000
- Production: Vercel domain (https://...)
- Add both to allowed_origins during development
- CI/CD: Replace localhost:3000 with production domain

**Configuration**:
```python
from config import get_settings

settings = get_settings()

allow_origins = [
    "http://localhost:3000",  # Always allow local dev
    settings.FRONTEND_URL,    # From .env, includes production
]
```

---

## 10. Async Python: FastAPI + async/await for Better Concurrency

**Pattern**: Use async functions in FastAPI for handling concurrent requests efficiently.

**Example (Async)**:
```python
@app.post("/chat/message")
async def chat(request: ChatRequest):
    # async function can handle multiple requests concurrently
    # While waiting for OpenAI API, request is paused (not blocked)
    response = await client.chat.completions.create(model="gpt-4o", ...)
    return response
```

**Benefits**:
- Handle 100+ concurrent requests without threading complexity
- Each request paused while waiting for I/O (OpenAI API, database)
- Automatic request queuing by Uvicorn
- Better resource utilization (less memory than threads)
- Simpler code than threading (no locks, race conditions)

**When to Use**:
- FastAPI endpoints (always use async)
- Calling external APIs (OpenAI, database)
- Long-running I/O operations

**When NOT to Use**:
- CPU-bound work (numeric computation) — use threads/processes
- Legacy synchronous libraries without async support

**Common Pattern**:
```python
async def handler():
    # I/O operations: database, API calls, file reading
    data = await db.query(...)
    response = await api.fetch(...)
    return data + response

# CPU operations: math, regex, text processing
def handler():
    result = expensive_calculation()
    return result
```

**Key Requirement**: All I/O libraries must be async-compatible (aiohttp, httpx, asyncpg, motor, etc.)

---

## 11. Semantic Versioning: MAJOR.MINOR.PATCH

**Pattern**: Version software using semantic versioning (X.Y.Z) to communicate changes.

**Scheme**:
- **MAJOR** (v1.x.x → v2.x.x): Breaking changes, incompatible API
- **MINOR** (v1.0.x → v1.1.x): New features, backward compatible
- **PATCH** (v1.0.x → v1.0.1): Bug fixes, no new features

**Examples**:
- v1.0.0 → Basic chat (first release)
- v1.0.1 → Bug fix in message rendering
- v1.1.0 → New feature (voice added → actually v2.0.0 in our case)
- v2.0.0 → Voice features (breaking change to UI)

**Documentation**:
- `docs/VERSIONS.md` tracks all versions
- Git tags: `git tag v1.0.0` for each version
- Commit message: "v1.0.0: Basic Chat SPA"

**For Our Project**:
```
v1.0.0 - Basic Chat
v2.0.0 - Voice Features
v3.0.0 - Authentication
v4.0.0 - LangChain + Database
v5.0.0 - RAG + Personalization
```

---

## 12. Minimal Dependencies: Do More With Less

**Pattern**: Add dependencies only when necessary, prefer built-in solutions.

**Example (Our Project)**:
- ✅ **Keep**: FastAPI (saves boilerplate), OpenAI SDK (required)
- ✅ **Keep**: TypeScript (type safety ROI is huge)
- ❌ **Avoid**: Redux (React Context sufficient for chat app)
- ❌ **Avoid**: axios (built-in fetch() works fine)
- ❌ **Avoid**: lodash (modern JS has most utilities)

**Benefit**: Fewer dependencies = smaller bundle, fewer security vulnerabilities, less maintenance

**Review Checklist**:
- Does the library solve a real problem?
- Is it actively maintained?
- Can it be replaced with built-in functionality?
- What's the bundle size impact?

---

## 13. Database Migrations: Version Control for Schema

**Pattern**: Track database schema changes in version-controlled migration files.

**Example** (Future, v4+):
```
backend/migrations/
├── 001_create_conversations.py
├── 002_create_message_table.py
├── 003_add_pgvector_extension.py
└── ...
```

**Tool Options**:
- Python: Alembic, SQLAlchemy migrate
- JavaScript: Knex.js, TypeORM

**Benefits**:
- Schema changes tracked in git (with history)
- Easy to roll back to previous schema
- New developers can bootstrap database with migrations
- CI/CD can auto-run migrations on deploy

**When to Use**: v4+ when adding PostgreSQL

---

## 14. Error Handling: Distinguish User vs. System Errors

**Pattern**: Return different HTTP status codes based on error type.

**Example**:
```python
# 400 Bad Request — user error (they can fix)
if not request.message:
    return {"error": "Message cannot be empty"}, 400

# 401 Unauthorized — authentication needed
if not is_authenticated():
    return {"error": "PIN required"}, 401

# 429 Too Many Requests — rate limited
if user_exceeded_rate_limit():
    return {"error": "Too many requests"}, 429

# 500 Internal Server Error — system error (can't fix)
if openai_api_down():
    return {"error": "Service temporarily unavailable"}, 500
```

**User-Facing Message**: Keep error messages helpful, not technical.
- ✅ "Message cannot be empty"
- ❌ "NoneType object is not subscriptable"

---

## 15. Logging: Different Levels for Different Severity

**Pattern**: Log messages with appropriate severity (DEBUG, INFO, WARNING, ERROR).

**Example**:
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Request received: %s", request.message)  # Dev info
logger.info("User sent message, awaiting OpenAI response")  # Key event
logger.warning("OpenAI response took 5 seconds")  # Unexpected but handled
logger.error("Failed to connect to OpenAI API", exc_info=True)  # Problem
```

**Configuration**:
```python
logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

**When to Use**: v4+ for monitoring and debugging in production

---

## How to Use This Document

**When starting a new project**:
- Review sections 1-5 (documentation, secrets, git, versioning, structure)
- Copy the 6-file documentation structure
- Set up environment secrets using 3-tier approach

**When designing API**:
- Review sections 6, 8, 9 (stateless design, deployment, CORS)
- Follow stateless request/response pattern
- Configure CORS early

**When writing code**:
- Review sections 7, 10, 14, 15 (types, async, errors, logging)
- Use TypeScript + Pydantic throughout
- Add async/await for I/O operations

**When deploying**:
- Review section 8 (auto-deployment)
- Test locally first
- Use semantic versioning
- Document in VERSIONS.md

---

## Living Document

This document grows as you learn new patterns. For each new project:
1. Review existing skills
2. Add 2-3 new learnings at the end
3. Update existing sections if you discover better approaches
4. Share with team members for feedback

**Future additions** (after v2-v5 are complete):
- Voice API integration patterns
- Authentication + JWT best practices
- Database transaction handling
- RAG evaluation metrics
- LangChain orchestration patterns
- Performance optimization techniques

---
