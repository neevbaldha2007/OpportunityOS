import uuid
from typing import Any, Generator
from sqlalchemy import create_engine, String, TypeDecorator, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Database engine
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class GUID(TypeDecorator):
    """Platform-independent GUID/UUID type.
    Uses PostgreSQL's native UUID type, otherwise stores as a 36-char string.
    """
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, str):
            try:
                return str(uuid.UUID(value))
            except ValueError:
                return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return str(value)


class JSONList(TypeDecorator):
    """Platform-independent List/Array type that stores list as JSON."""
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return []
        if isinstance(value, (list, tuple, set)):
            return [str(v) if isinstance(v, uuid.UUID) else v for v in value]
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return value


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
