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

# On Streamlit Cloud the source tree is read-only; write DB to /tmp instead
_IS_CLOUD = (
    os.environ.get("STREAMLIT_SHARING_MODE") == "1"
    or os.environ.get("HOME", "").startswith("/home/adminuser")
)


def get_default_db_url() -> str:
    """Return default SQLite database URL, cloud-safe."""
    if _IS_CLOUD:
        db_dir = Path("/tmp/aegis_data")
    else:
        db_dir = REPO_ROOT / "dashboard"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_file = db_dir / "aegis_safety.db"
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
