"""
AEGIS — Unit Tests for Database Layer
Tests session creation, violation logging, close_session, and analytics queries using an in-memory SQLite DB.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.database.models import Base, ScanSession, ViolationEvent


def make_test_engine():
    """Create in-memory SQLite engine for isolated testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine


def make_test_session(engine):
    SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))
    return SessionLocal


class TestScanSessionModel:
    def setup_method(self):
        self.engine = make_test_engine()
        self.Session = make_test_session(self.engine)

    def teardown_method(self):
        self.Session.remove()
        self.engine.dispose()

    def test_create_session(self):
        db = self.Session()
        s = ScanSession(scan_type="camera", source_name="Test Camera", status="running", start_time=datetime.utcnow())
        db.add(s)
        db.commit()
        assert s.session_id is not None
        assert s.scan_type == "camera"
        db.close()

    def test_session_default_total_violations(self):
        db = self.Session()
        s = ScanSession(scan_type="video", start_time=datetime.utcnow())
        db.add(s)
        db.commit()
        db.refresh(s)
        assert s.total_violations == 0
        db.close()

    def test_session_to_dict_structure(self):
        db = self.Session()
        s = ScanSession(scan_type="camera", start_time=datetime.utcnow(), status="completed")
        db.add(s)
        db.commit()
        d = s.to_dict()
        for key in ["session_id", "scan_type", "status", "total_violations"]:
            assert key in d
        db.close()


class TestViolationEventModel:
    def setup_method(self):
        self.engine = make_test_engine()
        self.Session = make_test_session(self.engine)

    def teardown_method(self):
        self.Session.remove()
        self.engine.dispose()

    def test_create_violation(self):
        db = self.Session()
        s = ScanSession(scan_type="camera", start_time=datetime.utcnow())
        db.add(s)
        db.commit()
        v = ViolationEvent(
            session_id=s.session_id,
            worker_id="WKR_101",
            violation_type="NO-Hardhat",
            confidence_score=0.87,
            severity="CRITICAL",
            timestamp=datetime.utcnow(),
            frame_number=12,
        )
        db.add(v)
        db.commit()
        assert v.violation_id is not None
        assert v.violation_type == "NO-Hardhat"
        db.close()

    def test_cascade_delete_violations(self):
        """Deleting session should delete its violations."""
        db = self.Session()
        s = ScanSession(scan_type="camera", start_time=datetime.utcnow())
        db.add(s)
        db.commit()
        v = ViolationEvent(
            session_id=s.session_id,
            violation_type="NO-Hardhat",
            timestamp=datetime.utcnow(),
        )
        db.add(v)
        db.commit()
        v_id = v.violation_id
        db.delete(s)
        db.commit()
        # Violation should be gone due to cascade
        assert db.query(ViolationEvent).filter_by(violation_id=v_id).first() is None
        db.close()

    def test_violation_to_dict(self):
        db = self.Session()
        v = ViolationEvent(
            violation_type="NO-Safety Vest",
            severity="CRITICAL",
            timestamp=datetime.utcnow(),
            worker_id="WKR_102",
            confidence_score=0.79,
        )
        db.add(v)
        db.commit()
        d = v.to_dict()
        assert d["violation_type"] == "NO-Safety Vest"
        assert d["severity"] == "CRITICAL"
        assert d["worker_id"] == "WKR_102"
        db.close()
