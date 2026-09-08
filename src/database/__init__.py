"""
AEGIS Database Package
"""

from src.database.connection import get_default_db_url, init_database
from src.database.models import Base, ScanSession, ViolationEvent
from src.database.repository import (
    close_session,
    create_session,
    get_analytics,
    get_db_session,
    get_recent_sessions,
    get_session_violations,
    log_violation,
)

__all__ = [
    "init_database",
    "get_default_db_url",
    "Base",
    "ScanSession",
    "ViolationEvent",
    "get_db_session",
    "create_session",
    "close_session",
    "log_violation",
    "get_recent_sessions",
    "get_session_violations",
    "get_analytics",
]
