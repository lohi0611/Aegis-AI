"""
AEGIS Safety Intelligence — Database Access Layer
Bridge connecting Streamlit UI to the central src.database ORM repository.
"""
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Ensure project root is in sys.path
_current_dir = Path(__file__).resolve().parent
_project_root = _current_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    from src.database import (
        init_database,
        create_session as create_scan_session,
        close_session as close_scan_session,
        log_violation as log_violation_db,
        get_recent_sessions,
        get_session_violations,
        get_analytics,
        ScanSession,
        ViolationEvent,
    )
    DB_AVAILABLE = True
except Exception as _e:
    print(f"[AEGIS DB Warning] Failed to initialize SQLAlchemy DB: {_e}")
    DB_AVAILABLE = False

    def create_scan_session(scan_type: str = "camera", source_name: Optional[str] = None):
        return None

    def close_scan_session(session_id: int, total_frames: int = 0, total_violations: int = 0, status: str = "completed"):
        return False

    def log_violation_db(session_id, worker_id, violation_type, timestamp=None, frame_number=0, confidence=0.0, bbox=None, snapshot_path=None):
        return None

    def get_recent_sessions(limit: int = 30):
        return []

    def get_session_violations(session_id: int):
        return []

    def get_analytics():
        return {
            "total_scans": 0, "total_violations": 0, "violations_today": 0,
            "critical_violations": 0, "most_common": "N/A", "by_type": {}, "daily": [], "safety_score": 100.0
        }
