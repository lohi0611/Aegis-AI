"""
AEGIS — Database Connection Factory
Handles database initialization, connection pooling, and session creation.
"""
import os
from pathlib import Path
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.database.models import Base

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def get_default_db_url() -> str:
    """Return default SQLite database URL."""
    db_file = REPO_ROOT / "dashboard" / "aegis_safety.db"
    db_file.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_file.as_posix()}"


def init_database(db_url: Optional[str] = None):
    """
    Initialize SQLAlchemy database engine and create tables.
    Returns (engine, SessionLocal).
    """
    url = db_url or os.environ.get("DATABASE_URL") or get_default_db_url()
    
    # Fix postgres:// URL prefix if provided by older cloud services
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )

    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    SessionLocal = scoped_session(session_factory)

    return engine, SessionLocal
