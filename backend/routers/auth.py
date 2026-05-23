"""
Authentication router for Lenoir Chatbot.

Provides endpoints for:
- POST /auth/login: Verify passphrase + PIN, issue bearer token
- POST /auth/logout: Invalidate token by removing from Redis
- Helper function to check if a request is from an authenticated owner

Design:
- Tokens are stored in Redis with TTL (default 24 hours)
- No token for guests — absence of Authorization header = guest mode
- Simple bearer token approach (stateless, no JWT overhead)
"""

import secrets
import hashlib
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from config import get_settings
from cache import cache_set, cache_get, cache_delete

router = APIRouter()
settings = get_settings()


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""
    passphrase: str
    pin: str


class LoginResponse(BaseModel):
    """Response body for POST /auth/login."""
    token: str
    is_owner: bool


class LogoutResponse(BaseModel):
    """Response body for POST /auth/logout."""
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    Authenticate owner with hashed PIN (SHA-256).

    v4 Flow:
    1. Hash the provided passphrase with SHA-256
    2. Compare to OWNER_API_KEY_HASH stored in config
    3. If match, generate token and store in Redis with TTL
    4. Return token to client

    Args:
        request: LoginRequest with passphrase (PIN as string) and optional pin field

    Returns:
        LoginResponse with token and is_owner: true

    Raises:
        HTTPException(401): If credentials are incorrect

    Example:
        POST /auth/login
        {
            "passphrase": "3114",
            "pin": ""
        }
    """
    if not settings.OWNER_API_KEY_HASH:
        raise HTTPException(status_code=500, detail="Authentication not configured")

    # Hash the provided passphrase and compare to stored hash
    provided_hash = hashlib.sha256(request.passphrase.encode()).hexdigest()

    if provided_hash != settings.OWNER_API_KEY_HASH:
        raise HTTPException(status_code=401, detail="Incorrect PIN")

    # Generate token and store in Redis with TTL
    token = secrets.token_urlsafe(32)
    await cache_set(
        key=f"auth:{token}",
        value={"is_owner": True},
        ttl=settings.AUTH_TOKEN_TTL
    )

    return LoginResponse(token=token, is_owner=True)


@router.post("/logout", response_model=LogoutResponse)
async def logout(request: Request) -> LogoutResponse:
    """
    Invalidate the current session token.

    Flow:
    1. Extract Authorization header (Bearer {token})
    2. Check if token exists in Redis
    3. If exists, delete it (logout complete)
    4. If doesn't exist, return 401

    Args:
        request: FastAPI Request object (reads Authorization header)

    Returns:
        LogoutResponse with success message

    Raises:
        HTTPException(403): If Authorization header is missing
        HTTPException(401): If token doesn't exist in Redis

    Example:
        POST /auth/logout
        Authorization: Bearer 5A8K9...z2Q1x

        200 OK
        {
            "message": "logged out"
        }
    """
    # Extract Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Missing Authorization header")

    token = auth_header.removeprefix("Bearer ").strip()

    # Check if token exists in Redis
    token_data = await cache_get(f"auth:{token}")
    if token_data is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Delete token
    await cache_delete(f"auth:{token}")

    return LogoutResponse(message="logged out")


async def get_is_owner(request: Request) -> bool:
    """
    Check if the request contains a valid owner token.

    Helper function for other routers to determine if user is authenticated as owner.
    Reads the Authorization header and checks if token exists in Redis.

    Args:
        request: FastAPI Request object

    Returns:
        bool: True if token is valid (owner), False otherwise (guest)

    Example usage in other routers:
        @router.post("/chat/message")
        async def chat(request: Request):
            is_owner = await get_is_owner(request)
            system_prompt = OWNER_PROMPT if is_owner else GUEST_PROMPT
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False

    token = auth_header.removeprefix("Bearer ").strip()
    token_data = await cache_get(f"auth:{token}")
    return token_data is not None
