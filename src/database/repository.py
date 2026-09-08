"""
AEGIS — Database Repository & Data Access Layer
Encapsulates CRUD operations, session lifecycle, and analytics aggregation queries.
"""

import hashlib
import secrets
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc, func

from src.database.connection import init_database
from src.database.models import ScanSession, User, ViolationEvent

# Global database access objects
_engine = None
_SessionLocal = None


def get_db_session():
    """Get active scoped database session."""
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine, _SessionLocal = init_database()
    return _SessionLocal()


def create_session(
    scan_type: str = "camera", source_name: Optional[str] = None
) -> Optional[int]:
    """Create a new ScanSession record and return session_id."""
    db = get_db_session()
    try:
        session_obj = ScanSession(
            scan_type=scan_type,
            source_name=source_name,
            start_time=datetime.utcnow(),
            status="running",
        )
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)
        return session_obj.session_id
    except Exception as e:
        db.rollback()
        print(f"[AEGIS-DB Error] Failed to create session: {e}")
        return None
    finally:
        db.close()


def close_session(
    session_id: int,
    total_frames: int = 0,
    total_violations: int = 0,
    status: str = "completed",
) -> bool:
    """Close and finalize a ScanSession record."""
    db = get_db_session()
    try:
        session_obj = (
            db.query(ScanSession).filter(ScanSession.session_id == session_id).first()
        )
        if session_obj:
            now = datetime.utcnow()
            session_obj.end_time = now
            session_obj.duration_seconds = (
                now - session_obj.start_time
            ).total_seconds()
            session_obj.total_frames = total_frames
            session_obj.total_violations = total_violations
            session_obj.status = status
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"[AEGIS-DB Error] Failed to close session {session_id}: {e}")
        return False
    finally:
        db.close()


def log_violation(
    session_id: Optional[int],
    worker_id: str,
    violation_type: str,
    timestamp: Optional[datetime] = None,
    frame_number: int = 0,
    confidence: float = 0.0,
    bbox: Optional[List[int]] = None,
    snapshot_path: Optional[str] = None,
    severity: Optional[str] = None,
) -> Optional[int]:
    """Log an individual violation event."""
    if severity is None:
        severity = (
            "CRITICAL"
            if ("Hardhat" in str(violation_type) or "Vest" in str(violation_type))
            else "HIGH"
        )

    bbox = bbox or [0, 0, 0, 0]
    ts = timestamp or datetime.utcnow()

    db = get_db_session()
    try:
        event = ViolationEvent(
            session_id=int(session_id) if session_id is not None else None,
            worker_id=str(worker_id) if worker_id is not None else "Unknown",
            violation_type=str(violation_type),
            confidence_score=float(confidence),
            severity=str(severity),
            timestamp=ts,
            frame_number=int(frame_number),
            bbox_x1=int(bbox[0]) if len(bbox) > 0 else 0,
            bbox_y1=int(bbox[1]) if len(bbox) > 1 else 0,
            bbox_x2=int(bbox[2]) if len(bbox) > 2 else 0,
            bbox_y2=int(bbox[3]) if len(bbox) > 3 else 0,
            snapshot_path=str(snapshot_path) if snapshot_path else None,
            status="Violation",
        )
        db.add(event)

        # Increment session violation count if session active
        if session_id is not None:
            s_obj = (
                db.query(ScanSession)
                .filter(ScanSession.session_id == int(session_id))
                .first()
            )
            if s_obj:
                s_obj.total_violations = (s_obj.total_violations or 0) + 1

        db.commit()
        db.refresh(event)
        return event.violation_id
    except Exception as e:
        db.rollback()
        print(f"[AEGIS-DB Error] Failed to log violation: {e}")
        return None
    finally:
        db.close()


def get_recent_sessions(limit: int = 30) -> List[Dict[str, Any]]:
    """Retrieve recent scan sessions."""
    db = get_db_session()
    try:
        sessions = (
            db.query(ScanSession)
            .order_by(desc(ScanSession.session_id))
            .limit(limit)
            .all()
        )
        return [s.to_dict() for s in sessions]
    except Exception as e:
        print(f"[AEGIS-DB Error] get_recent_sessions: {e}")
        return []
    finally:
        db.close()


def get_session_violations(session_id: int) -> List[Dict[str, Any]]:
    """Retrieve all violations belonging to a session."""
    db = get_db_session()
    try:
        violations = (
            db.query(ViolationEvent)
            .filter(ViolationEvent.session_id == int(session_id))
            .order_by(ViolationEvent.timestamp.asc())
            .all()
        )
        return [v.to_dict() for v in violations]
    except Exception as e:
        print(f"[AEGIS-DB Error] get_session_violations: {e}")
        return []
    finally:
        db.close()


def get_analytics() -> Dict[str, Any]:
    """Calculate aggregated safety metrics for analytics dashboards."""
    db = get_db_session()
    try:
        total_scans = db.query(ScanSession).count()
        total_violations = db.query(ViolationEvent).count()

        today_start = datetime.combine(date.today(), datetime.min.time())
        violations_today = (
            db.query(ViolationEvent)
            .filter(ViolationEvent.timestamp >= today_start)
            .count()
        )

        critical_violations = (
            db.query(ViolationEvent)
            .filter(ViolationEvent.severity == "CRITICAL")
            .count()
        )

        # By type distribution
        by_type_query = (
            db.query(
                ViolationEvent.violation_type, func.count(ViolationEvent.violation_id)
            )
            .group_by(ViolationEvent.violation_type)
            .all()
        )
        by_type = {t: c for t, c in by_type_query}
        most_common = max(by_type, key=by_type.get) if by_type else "N/A"

        # Daily trend (last 14 days)
        cutoff = datetime.utcnow() - timedelta(days=14)
        daily_query = (
            db.query(
                func.date(ViolationEvent.timestamp).label("d"),
                func.count(ViolationEvent.violation_id).label("c"),
            )
            .filter(ViolationEvent.timestamp >= cutoff)
            .group_by("d")
            .order_by("d")
            .all()
        )
        daily = [{"date": str(r.d), "count": int(r.c)} for r in daily_query]

        # Safety score calculation
        total_frames = db.query(func.sum(ScanSession.total_frames)).scalar() or 0
        safety_score = (
            max(0.0, round((1.0 - total_violations / max(total_frames, 1)) * 100.0, 1))
            if total_frames > 0
            else 100.0
        )

        return {
            "total_scans": total_scans,
            "total_violations": total_violations,
            "violations_today": violations_today,
            "critical_violations": critical_violations,
            "most_common": most_common,
            "by_type": by_type,
            "daily": daily,
            "safety_score": safety_score,
        }
    except Exception as e:
        print(f"[AEGIS-DB Error] get_analytics: {e}")
        return {
            "total_scans": 0,
            "total_violations": 0,
            "violations_today": 0,
            "critical_violations": 0,
            "most_common": "N/A",
            "by_type": {},
            "daily": [],
            "safety_score": 100.0,
        }
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
#  USER AUTHENTICATION & MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Cryptographically hash password using PBKDF2-HMAC-SHA256 (100k iterations).
    Returns (hex_hash, hex_salt).
    """
    if salt is None:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return key.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify password against stored hash and salt."""
    calc_hash, _ = hash_password(password, salt=salt)
    return secrets.compare_digest(calc_hash, password_hash)


def register_user(
    email: str,
    password: str,
    full_name: str,
    role: str = "Safety Inspector",
) -> Optional[Dict[str, Any]]:
    """Register a new user record. Returns user dict on success, None if email taken."""
    db = get_db_session()
    try:
        clean_email = email.strip().lower()
        existing = db.query(User).filter(func.lower(User.email) == clean_email).first()
        if existing:
            return None

        pwd_hash, salt = hash_password(password)
        user = User(
            email=clean_email,
            full_name=full_name.strip(),
            password_hash=pwd_hash,
            salt=salt,
            role=role.strip(),
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.to_dict()
    except Exception as e:
        db.rollback()
        print(f"[AEGIS-DB Error] register_user: {e}")
        return None
    finally:
        db.close()


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user credentials. Returns user dict on success, None on failure."""
    db = get_db_session()
    try:
        clean_email = email.strip().lower()
        user = db.query(User).filter(func.lower(User.email) == clean_email).first()
        if not user:
            return None

        if verify_password(password, user.password_hash, user.salt):
            user.last_login = datetime.utcnow()
            db.commit()
            return user.to_dict()
        return None
    except Exception as e:
        print(f"[AEGIS-DB Error] authenticate_user: {e}")
        return None
    finally:
        db.close()


def seed_default_user_if_empty():
    """Seed a default administrative user if no users exist."""
    db = get_db_session()
    try:
        count = db.query(func.count(User.user_id)).scalar()
        if count == 0:
            pwd_hash, salt = hash_password("Admin@1234")
            admin = User(
                email="admin@aegis.ai",
                full_name="Alex Vance (Chief Safety Officer)",
                password_hash=pwd_hash,
                salt=salt,
                role="Site EHS Director",
                created_at=datetime.utcnow(),
            )
            db.add(admin)
            db.commit()
            print("[AEGIS] Default demo user seeded: admin@aegis.ai / Admin@1234")
    except Exception as e:
        db.rollback()
        print(f"[AEGIS-DB Error] seed_default_user_if_empty: {e}")
    finally:
        db.close()

