"""
Lenoir Assistant API - Main Application Entry Point (v5)

This is the FastAPI application factory and configuration. It handles:
- CORS middleware for cross-origin requests from frontend
- Router registration for all API endpoints
- Health check endpoint with Redis + PostgreSQL status monitoring

Configuration:
- Version: 5.0.0 (RAG system with pgvector + document management)
- Base URL: /chat (all chat endpoints prefixed with /chat), /documents (RAG)
- Health check: /health (returns API, cache, and database status)
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from config import get_settings
from routers import chat, voice, auth, documents
from cache import is_redis_available
from db.session import get_db

settings = get_settings()
app = FastAPI(title="Lenoir Assistant API", version="5.0.0")

# ============================================================================
# CORS Middleware - Allow Frontend to Call This API
# ============================================================================
# CORS (Cross-Origin Resource Sharing) is required because the frontend
# (Vercel) and backend (Railway) are on different domains.
#
# Configuration:
# - allow_origins: Frontend URLs that can call this API
# - allow_credentials: Allow cookies/auth headers
# - allow_methods: All HTTP methods allowed (GET, POST, DELETE, etc.)
# - allow_headers: All headers allowed (Content-Type, Authorization, etc.)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API Routes Registration
# ============================================================================
# Include all routers. Routes are prefixed with their router prefix.
# Example: chat router has prefix="/chat", so endpoints are /chat/message
# voice router has prefix="/voice", so endpoints are /voice/transcribe and /voice/speak

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(documents.router)  # v5: RAG document management

# ============================================================================
# Health Check Endpoint - Includes Redis Status
# ============================================================================

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint for monitoring API status (v4: includes database).

    Returns API, Redis (cache), and PostgreSQL (database) status. Useful for:
    - Load balancer health checks (Railway, Vercel, etc.)
    - Monitoring cache and database connectivity
    - Debugging deployment issues

    Status Behavior:
    - Redis down: Returns "ok" + "redis": "disconnected" (graceful degradation)
    - Database down: Returns "ok" + "database": "disconnected" (blocks v4 features)
    - Both down: Returns "ok" + both "disconnected" (still alive)

    Returns:
        dict: Contains "status", "redis", and "database" status

    Example response:
        {
            "status": "ok",
            "redis": "connected",
            "database": "connected"
        }
    """
    # REDIS CHECK: Ping Redis to verify cache layer
    redis_status = "connected" if is_redis_available() else "disconnected"

    # DATABASE CHECK: Verify PostgreSQL connection with simple query
    db_status = "disconnected"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    return {
        "status": "ok",
        "redis": redis_status,
        "database": db_status
    }


# ============================================================================
# Application Startup
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
