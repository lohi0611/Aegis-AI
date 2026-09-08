"""
AEGIS Database Package
"""

from src.database.connection import get_default_db_url, init_database
from src.database.models import Base, ScanSession, User, ViolationEvent
from src.database.repository import (
    authenticate_user,
    close_session,
    create_session,
    get_analytics,
    get_db_session,
    get_recent_sessions,
    get_session_violations,
    log_violation,
    register_user,
    seed_default_user_if_empty,
)

__all__ = [
    "init_database",
    "get_default_db_url",
    "Base",
    "ScanSession",
    "ViolationEvent",
    "User",
    "get_db_session",
    "create_session",
    "close_session",
    "log_violation",
    "get_recent_sessions",
    "get_session_violations",
    "get_analytics",
    "authenticate_user",
    "register_user",
    "seed_default_user_if_empty",
]

