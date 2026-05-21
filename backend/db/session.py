from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import get_settings

settings = get_settings()

# Convert DATABASE_URL to async format if needed
db_url = settings.DATABASE_URL
if db_url and "postgresql://" in db_url and "postgresql+asyncpg://" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine with pool settings for Railway/cloud deployments
engine = create_async_engine(
    db_url or "postgresql+asyncpg://localhost/lenoir_chatbot",
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """Async dependency for FastAPI to inject DB session into routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
