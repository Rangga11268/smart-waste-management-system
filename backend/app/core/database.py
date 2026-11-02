"""Database connectivity, engine initialization with automatic SQLite fallback, and session management."""

import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

try:
    from app.core.config import settings
    from app.models.base import Base
except ImportError:
    from backend.app.core.config import settings
    from backend.app.models.base import Base

logger = logging.getLogger("swms.database")


def configure_sqlite_engine(sqlite_url: str) -> Engine:
    """Configure SQLite engine with threading and foreign key support."""
    is_memory = ":memory:" in sqlite_url
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool if is_memory else None,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    return engine


def create_app_engine(
    database_url: Optional[str] = None,
    fallback_url: Optional[str] = None,
) -> Engine:
    """Initialize database engine with active TCP probe and automatic SQLite fallback."""
    db_url = database_url or settings.DATABASE_URL
    fallback = fallback_url or settings.SQLITE_FALLBACK_URL

    if not db_url or db_url.startswith("sqlite"):
        logger.info("Configuring SQLite database engine: %s", db_url or fallback)
        return configure_sqlite_engine(db_url or fallback)

    # Attempt connection to primary database (e.g. PostgreSQL)
    temp_engine = None
    try:
        connect_args = {}
        if "postgresql" in db_url:
            connect_args["connect_timeout"] = 2
        temp_engine = create_engine(
            db_url,
            connect_args=connect_args,
            pool_pre_ping=True,
        )
        with temp_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected successfully to primary database: %s", db_url)
        return temp_engine
    except Exception as exc:
        if temp_engine is not None:
            temp_engine.dispose()
        logger.warning(
            "Primary database connection failed (%s: %s). Falling back to local SQLite: %s",
            type(exc).__name__,
            exc,
            fallback,
        )
        return configure_sqlite_engine(fallback)


engine = create_app_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """FastAPI dependency yielding a database session and safely closing on completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
