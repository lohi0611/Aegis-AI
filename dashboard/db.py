"""
AEGIS Safety Intelligence — Database Layer
Uses SQLAlchemy with SQLite by default.
Set DATABASE_URL env var to switch to PostgreSQL:
  DATABASE_URL=postgresql://user:pass@host/db
"""
import os
from datetime import datetime, date
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

# ── SQLAlchemy imports ──────────────────────────────────────────────────────
try:
    from sqlalchemy import (
        create_engine, Column, Integer, String, Float, DateTime,
        Text, ForeignKey, func, text
    )
    from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# ── Configuration ───────────────────────────────────────────────────────────
_current_dir = os.path.dirname(os.path.abspath(__file__))
_default_db  = f"sqlite:///{os.path.join(_current_dir, 'aegis_safety.db')}"
DATABASE_URL = os.environ.get("DATABASE_URL", _default_db)

# Heroku/Render give "postgres://" which SQLAlchemy 1.4+ requires as "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ── Engine + Session ────────────────────────────────────────────────────────
_engine = None
_SessionLocal = None
DB_AVAILABLE = False

if SQLALCHEMY_AVAILABLE:
    try:
        connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
        _engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
        _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
        DB_AVAILABLE = True
    except Exception as _e:
        print(f"[AEGIS DB] Engine creation failed: {_e}")

# ── ORM Models ──────────────────────────────────────────────────────────────
if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()

    class ScanSession(Base):
        __tablename__ = "scan_sessions"

        session_id      = Column(Integer, primary_key=True, autoincrement=True)
        scan_type       = Column(String(50), nullable=False)  # uploaded_video | laptop_camera | sample_video | local_webcam
        source_name     = Column(String(255))
        start_time      = Column(DateTime, nullable=False, default=datetime.utcnow)
        end_time        = Column(DateTime)
        duration_seconds= Column(Float)
        total_frames    = Column(Integer, default=0)
        total_violations= Column(Integer, default=0)
        status          = Column(String(20), default="running")  # running | completed | stopped
        created_at      = Column(DateTime, default=datetime.utcnow)

        violations = relationship("Violation", back_populates="session", cascade="all, delete-orphan")

    class Violation(Base):
        __tablename__ = "violations"

        violation_id    = Column(Integer, primary_key=True, autoincrement=True)
        session_id      = Column(Integer, ForeignKey("scan_sessions.session_id"), nullable=False)
        worker_id       = Column(String(20))
        violation_type  = Column(String(100), nullable=False)
        timestamp       = Column(DateTime, nullable=False)
        frame_number    = Column(Integer)
        confidence_score= Column(Float)
        x1 = Column(Integer); y1 = Column(Integer)
        x2 = Column(Integer); y2 = Column(Integer)
        severity        = Column(String(20), default="HIGH")   # CRITICAL | HIGH | MEDIUM
        snapshot_path   = Column(Text)
        status          = Column(String(20), default="Violation")
        created_at      = Column(DateTime, default=datetime.utcnow)

        session = relationship("ScanSession", back_populates="violations")

    # Create tables on first import
    try:
        Base.metadata.create_all(bind=_engine)
    except Exception as _e:
        print(f"[AEGIS DB] Table creation failed: {_e}")
        DB_AVAILABLE = False


# ── Context manager ─────────────────────────────────────────────────────────
@contextmanager
def get_db():
    if not DB_AVAILABLE or _SessionLocal is None:
        yield None
        return
    db: Session = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Helpers ─────────────────────────────────────────────────────────────────

def _severity_for(violation_type: str) -> str:
    """Derive severity from violation type."""
    critical = {"NO-Hardhat", "NO-Safety Vest"}
    if violation_type in critical:
        return "CRITICAL"
    return "HIGH"


def create_scan_session(scan_type: str, source_name: str) -> Optional[int]:
    """Open a new scan session. Returns session_id or None if DB unavailable."""
    if not DB_AVAILABLE:
        return None
    with get_db() as db:
        if db is None:
            return None
        s = ScanSession(
            scan_type=scan_type,
            source_name=source_name,
            start_time=datetime.utcnow(),
            status="running",
        )
        db.add(s)
        db.flush()
        sid = s.session_id
    return sid


def close_scan_session(session_id: int, total_frames: int, total_violations: int, status: str = "completed"):
    """Close a scan session — set end_time, duration, counts, status."""
    if not DB_AVAILABLE or session_id is None:
        return
    with get_db() as db:
        if db is None:
            return
        s = db.query(ScanSession).filter_by(session_id=session_id).first()
        if s:
            s.end_time = datetime.utcnow()
            s.duration_seconds = (s.end_time - s.start_time).total_seconds()
            s.total_frames = total_frames
            s.total_violations = total_violations
            s.status = status


def log_violation_db(
    session_id: int,
    worker_id: str,
    violation_type: str,
    timestamp: datetime,
    frame_number: int,
    confidence: float,
    bbox: List[int],          # [x1,y1,x2,y2]
    snapshot_path: str,
) -> Optional[int]:
    """Insert one violation event. Returns violation_id or None."""
    if not DB_AVAILABLE or session_id is None:
        return None
    with get_db() as db:
        if db is None:
            return None
        v = Violation(
            session_id=session_id,
            worker_id=worker_id,
            violation_type=violation_type,
            timestamp=timestamp,
            frame_number=frame_number,
            confidence_score=round(confidence, 4),
            x1=bbox[0], y1=bbox[1], x2=bbox[2], y2=bbox[3],
            severity=_severity_for(violation_type),
            snapshot_path=snapshot_path,
            status="Violation",
        )
        db.add(v)
        db.flush()
        vid = v.violation_id
    return vid


def get_session_violations(session_id: int) -> List[Dict]:
    """Return all violations for a session as list of dicts."""
    if not DB_AVAILABLE:
        return []
    with get_db() as db:
        if db is None:
            return []
        rows = db.query(Violation).filter_by(session_id=session_id).order_by(Violation.timestamp).all()
        return [_v_to_dict(r) for r in rows]


def get_recent_sessions(limit: int = 20) -> List[Dict]:
    """Return recent scan sessions as list of dicts."""
    if not DB_AVAILABLE:
        return []
    with get_db() as db:
        if db is None:
            return []
        rows = (
            db.query(ScanSession)
            .order_by(ScanSession.created_at.desc())
            .limit(limit)
            .all()
        )
        return [_s_to_dict(r) for r in rows]


def get_analytics() -> Dict[str, Any]:
    """Return aggregate analytics from DB."""
    if not DB_AVAILABLE:
        return _empty_analytics()
    with get_db() as db:
        if db is None:
            return _empty_analytics()
        today = date.today()

        total_scans      = db.query(func.count(ScanSession.session_id)).scalar() or 0
        total_violations = db.query(func.count(Violation.violation_id)).scalar() or 0

        violations_today = (
            db.query(func.count(Violation.violation_id))
            .filter(func.date(Violation.timestamp) == today)
            .scalar() or 0
        )

        critical_violations = (
            db.query(func.count(Violation.violation_id))
            .filter(Violation.severity == "CRITICAL")
            .scalar() or 0
        )

        # Most common violation type
        most_common_row = (
            db.query(Violation.violation_type, func.count(Violation.violation_id).label("cnt"))
            .group_by(Violation.violation_type)
            .order_by(text("cnt DESC"))
            .first()
        )
        most_common = most_common_row[0] if most_common_row else "N/A"

        # Violations by type
        type_rows = (
            db.query(Violation.violation_type, func.count(Violation.violation_id).label("cnt"))
            .group_by(Violation.violation_type)
            .all()
        )
        by_type = {r[0]: r[1] for r in type_rows}

        # Violations per day (last 30 days)
        daily_rows = (
            db.query(func.date(Violation.timestamp).label("day"), func.count(Violation.violation_id).label("cnt"))
            .group_by(text("day"))
            .order_by(text("day"))
            .limit(30)
            .all()
        )
        daily = [{"date": str(r[0]), "count": r[1]} for r in daily_rows]

        # Safety score: compliant frames / total frames from all completed sessions
        frames_total = db.query(func.sum(ScanSession.total_frames)).scalar() or 0
        frames_violated = db.query(func.sum(ScanSession.total_violations)).scalar() or 0
        safety_score = max(0, round((1 - frames_violated / max(frames_total, 1)) * 100, 1))

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


# ── Internal converters ──────────────────────────────────────────────────────
def _v_to_dict(v) -> Dict:
    return {
        "violation_id":   v.violation_id,
        "session_id":     v.session_id,
        "worker_id":      v.worker_id,
        "violation_type": v.violation_type,
        "timestamp":      str(v.timestamp),
        "frame_number":   v.frame_number,
        "confidence":     v.confidence_score,
        "x1": v.x1, "y1": v.y1, "x2": v.x2, "y2": v.y2,
        "severity":       v.severity,
        "snapshot_path":  v.snapshot_path,
        "status":         v.status,
    }

def _s_to_dict(s) -> Dict:
    return {
        "session_id":       s.session_id,
        "scan_type":        s.scan_type,
        "source_name":      s.source_name,
        "start_time":       str(s.start_time),
        "end_time":         str(s.end_time) if s.end_time else None,
        "duration_seconds": s.duration_seconds,
        "total_frames":     s.total_frames,
        "total_violations": s.total_violations,
        "status":           s.status,
        "created_at":       str(s.created_at),
    }

def _empty_analytics() -> Dict:
    return {
        "total_scans": 0, "total_violations": 0, "violations_today": 0,
        "critical_violations": 0, "most_common": "N/A",
        "by_type": {}, "daily": [], "safety_score": 100.0,
    }
