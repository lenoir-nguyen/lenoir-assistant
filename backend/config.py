"""
Configuration management for the Lenoir Assistant API (v5).

This module uses Pydantic Settings (v2) to manage environment variables
from the .env file. All sensitive configuration (API keys, URLs) should
be stored in .env and loaded at startup.

Environment Variables (from .env):
- OPENAI_API_KEY: Required. Secret key for OpenAI API access
- DEBUG: Optional. Enable debug mode (default: false)
- FRONTEND_URL: Optional. Frontend origin for CORS (default: http://localhost:3000)
- REDIS_URL: Optional. Redis connection URL (default: redis://localhost:6379)
- DATABASE_URL: Required (v4+). PostgreSQL connection string
- DATABASE_POOL_SIZE: Optional. SQLAlchemy connection pool size (default: 5)
- DATABASE_MAX_OVERFLOW: Optional. Max overflow connections (default: 10)
- DATABASE_ECHO: Optional. Log SQL queries (default: false)

RAG Configuration (v5):
- RAG_ENABLED: Enable/disable RAG system (default: true)
- STORAGE_TYPE: 'local' for development, 's3' for production (default: local)
- DOCUMENT_UPLOAD_DIR: Where to store files (local storage only)
- MAX_DOCUMENT_SIZE_MB: Max file size in MB (default: 10)
- AWS_ACCESS_KEY_ID: AWS credentials (S3 storage only)
- AWS_SECRET_ACCESS_KEY: AWS credentials (S3 storage only)
- AWS_S3_BUCKET: S3 bucket name (S3 storage only)
- AWS_S3_REGION: AWS region (default: us-east-1)
- CHUNK_SIZE: Tokens per chunk (default: 1024)
- CHUNK_OVERLAP: Token overlap between chunks (default: 100)
- MAX_CHUNKS_PER_QUERY: Top N chunks to retrieve (default: 10)

Note: .env is git-ignored and should never be committed.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from .env file (v5: RAG system).

    Uses Pydantic v2 ConfigDict for configuration (Pydantic v2 syntax, not v1).
    All fields are required unless a default value is provided.

    Attributes:
        OPENAI_API_KEY (str): Secret API key for OpenAI. Must be set in .env
        DEBUG (bool): Enable debug mode for development (default: False)
        FRONTEND_URL (str): Frontend origin for CORS policy (default: http://localhost:3000)
        tts_voice (str): OpenAI TTS voice for text-to-speech synthesis (default: "nova")
        OWNER_API_KEY_HASH (str): SHA-256 hash of owner PIN for authentication (v4)
        AUTH_TOKEN_TTL (int): Auth token lifetime in seconds (default: 86400 = 24 hours)
        REDIS_URL (str): Redis connection string (default: redis://localhost:6379)
        DATABASE_URL (str): PostgreSQL connection URL (v4+, required for persistence)
        DATABASE_POOL_SIZE (int): SQLAlchemy connection pool size (default: 5)
        DATABASE_MAX_OVERFLOW (int): Max overflow connections beyond pool size (default: 10)
        DATABASE_ECHO (bool): Log all SQL queries to stdout (default: False)

        FACT_CACHE_TTL_OWNER (int): Owner fact cache lifetime in seconds (default: 86400)
        FACT_CACHE_TTL_GUEST (int): Guest fact cache lifetime in seconds (default: 3600)
        FACT_CACHE_MAX_ITEMS (int): Max facts stored per session (default: 50)
        FACT_EXTRACTION_ENABLED (bool): Enable/disable fact extraction (v4.1, default: True)

        RAG_ENABLED (bool): Enable/disable RAG system (v5, default: True)
        STORAGE_TYPE (str): 'local' or 's3' for file storage (default: "local")
        DOCUMENT_UPLOAD_DIR (str): Directory for local file storage (default: "./uploads")
        MAX_DOCUMENT_SIZE_MB (int): Max file size in MB (default: 10)
        AWS_ACCESS_KEY_ID (str): AWS credentials for S3 (optional)
        AWS_SECRET_ACCESS_KEY (str): AWS credentials for S3 (optional)
        AWS_S3_BUCKET (str): S3 bucket name (optional)
        AWS_S3_REGION (str): AWS region (default: "us-east-1")
        CHUNK_SIZE (int): Tokens per document chunk (default: 1024)
        CHUNK_OVERLAP (int): Token overlap between chunks (default: 100)
        MAX_CHUNKS_PER_QUERY (int): Top N chunks to retrieve per query (default: 10)
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
    FACT_CACHE_TTL_OWNER: int = 86400  # Owner fact cache lifetime (24 hours)
    FACT_CACHE_TTL_GUEST: int = 3600  # Guest fact cache lifetime (1 hour)
    FACT_CACHE_MAX_ITEMS: int = 50  # Max facts stored per session
    FACT_EXTRACTION_ENABLED: bool = True  # Enable/disable fact extraction

    # RAG Configuration (v5)
    RAG_ENABLED: bool = True  # Enable/disable RAG system
    STORAGE_TYPE: str = "local"  # 'local' or 's3'
    DOCUMENT_UPLOAD_DIR: str = "./uploads"  # Local storage directory
    MAX_DOCUMENT_SIZE_MB: int = 10  # Max file size
    # AWS S3 credentials (only needed if STORAGE_TYPE=s3)
    AWS_ACCESS_KEY_ID: str = ""  # AWS access key (optional)
    AWS_SECRET_ACCESS_KEY: str = ""  # AWS secret key (optional)
    AWS_S3_BUCKET: str = ""  # S3 bucket name (optional)
    AWS_S3_REGION: str = "us-east-1"  # AWS region
    # Chunking configuration
    CHUNK_SIZE: int = 1024  # Tokens per chunk
    CHUNK_OVERLAP: int = 100  # Token overlap between chunks
    MAX_CHUNKS_PER_QUERY: int = 10  # Top N chunks to retrieve

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
