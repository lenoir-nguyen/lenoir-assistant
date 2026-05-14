import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/lenoir_chatbot"

    # OpenAI API
    OPENAI_API_KEY: str = ""

    # Identity & Auth
    OWNER_PIN_HASH: str = ""  # bcrypt hash of the PIN (set this in .env)

    # LangChain & LLM
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: str = "false"

    # Server
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
