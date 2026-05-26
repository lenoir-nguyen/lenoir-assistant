import os
from .models import Base, Session, Message, PersonalFact, Document, DocumentChunk

# Only import session components if not running under Alembic
if not os.environ.get("ALEMBIC_RUNNING"):
    from .session import AsyncSessionLocal, engine, get_db
else:
    AsyncSessionLocal = None
    engine = None
    get_db = None

__all__ = [
    "Base",
    "Session",
    "Message",
    "PersonalFact",
    "Document",
    "DocumentChunk",
    "AsyncSessionLocal",
    "engine",
    "get_db",
]
