"""
Configuration management for the Lenoir Assistant API.

This module uses Pydantic Settings (v2) to manage environment variables
from the .env file. All sensitive configuration (API keys, URLs) should
be stored in .env and loaded at startup.

Environment Variables (from .env):
- OPENAI_API_KEY: Required. Secret key for OpenAI API access
- DEBUG: Optional. Enable debug mode (default: false)
- FRONTEND_URL: Optional. Frontend origin for CORS (default: http://localhost:3000)
- REDIS_URL: Optional. Redis connection URL (default: redis://localhost:6379)
- DATABASE_URL: Required (v4+). PostgreSQL connection string (e.g., postgresql://user:pass@host/dbname)
- DATABASE_POOL_SIZE: Optional. SQLAlchemy connection pool size (default: 5)
- DATABASE_MAX_OVERFLOW: Optional. Max overflow connections (default: 10)
- DATABASE_ECHO: Optional. Log SQL queries (default: false)

Note: .env is git-ignored and should never be committed.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from .env file.

    Uses Pydantic v2 ConfigDict for configuration (Pydantic v2 syntax, not v1).
    All fields are required unless a default value is provided.

    Attributes:
        OPENAI_API_KEY (str): Secret API key for OpenAI. Must be set in .env
        DEBUG (bool): Enable debug mode for development (default: False)
        FRONTEND_URL (str): Frontend origin for CORS policy (default: http://localhost:3000)
        tts_voice (str): OpenAI TTS voice for text-to-speech synthesis (default: "nova")
                        Valid options: alloy, echo, fable, onyx, nova, shimmer
        OWNER_API_KEY_HASH (str): SHA-256 hash of owner PIN for authentication (v4 feature)
        AUTH_TOKEN_TTL (int): Auth token lifetime in seconds (default: 86400 = 24 hours)
        REDIS_URL (str): Redis connection string (default: redis://localhost:6379)
        DATABASE_URL (str): PostgreSQL connection URL (v4+ feature, required for persistence)
        DATABASE_POOL_SIZE (int): SQLAlchemy connection pool size (default: 5)
        DATABASE_MAX_OVERFLOW (int): Max overflow connections beyond pool size (default: 10)
        DATABASE_ECHO (bool): Log all SQL queries to stdout (default: False)
    """

    OPENAI_API_KEY: str
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"
    tts_voice: str = "nova"  # OpenAI TTS voice for v2 voice output feature
    OWNER_API_KEY_HASH: str = ""  # SHA-256 hash of owner PIN for authentication (v4)
    AUTH_TOKEN_TTL: int = 86400  # token lifetime in seconds (24 hours)
    REDIS_URL: str = "redis://localhost:6379"  # v3 cache layer
    DATABASE_URL: str = ""  # v4: PostgreSQL connection string (required for persistence)
    DATABASE_POOL_SIZE: int = 5  # v4: SQLAlchemy connection pool size
    DATABASE_MAX_OVERFLOW: int = 10  # v4: Max overflow connections
    DATABASE_ECHO: bool = False  # v4: Log SQL queries for debugging
    FACT_CACHE_TTL: int = 28800  # Fact cache lifetime in seconds (8 hours)
    FACT_CACHE_MAX_ITEMS: int = 50  # Max facts stored per session
    FACT_EXTRACTION_ENABLED: bool = True  # Enable/disable fact extraction

    # Pydantic v2 configuration
    # env_file: Load variables from .env file in this directory
    # case_sensitive: Environment variable names are case-sensitive
    model_config = ConfigDict(env_file=".env", case_sensitive=True)


def get_settings():
    """
    Factory function to create and return Settings instance.

    This is called once at module startup to load configuration.
    The Settings object is then used throughout the application
    (e.g., settings.OPENAI_API_KEY for API initialization).

    Returns:
        Settings: Singleton configuration object with all env vars loaded

    Example:
        >>> settings = get_settings()
        >>> api_key = settings.OPENAI_API_KEY
    """
    return Settings()
