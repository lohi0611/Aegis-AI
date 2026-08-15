"""
AEGIS — Database Schema & ORM Models
Defines ScanSession and ViolationEvent relational tables with indexes and foreign keys.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Index, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ScanSession(Base):
    """Represents a continuous monitoring scan session."""
    __tablename__ = "scan_sessions"

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    scan_type = Column(String(64), nullable=False, default="camera")
    source_name = Column(String(256), nullable=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True, default=0.0)
    total_frames = Column(Integer, nullable=False, default=0)
    total_violations = Column(Integer, nullable=False, default=0)
    status = Column(String(32), nullable=False, default="running", index=True)

    # Relationships
    violations = relationship("ViolationEvent", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_session_status_time", "status", "start_time"),
    )

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "scan_type": self.scan_type,
            "source_name": self.source_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "total_frames": self.total_frames,
            "total_violations": self.total_violations,
            "status": self.status,
        }


class ViolationEvent(Base):
    """Represents an individual confirmed PPE violation event."""
    __tablename__ = "violations"

    violation_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("scan_sessions.session_id", ondelete="CASCADE"), nullable=True, index=True)
    worker_id = Column(String(64), nullable=True, index=True)
    violation_type = Column(String(64), nullable=False, index=True)
    confidence_score = Column(Float, nullable=False, default=0.0)
    severity = Column(String(32), nullable=False, default="HIGH", index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    frame_number = Column(Integer, nullable=False, default=0)
    
    # Bounding box coordinates
    bbox_x1 = Column(Integer, nullable=True)
    bbox_y1 = Column(Integer, nullable=True)
    bbox_x2 = Column(Integer, nullable=True)
    bbox_y2 = Column(Integer, nullable=True)
    
    snapshot_path = Column(String(512), nullable=True)
    status = Column(String(32), nullable=False, default="Violation")

    # Relationships
    session = relationship("ScanSession", back_populates="violations")

    __table_args__ = (
        Index("idx_violation_type_time", "violation_type", "timestamp"),
        Index("idx_worker_time", "worker_id", "timestamp"),
    )

    def to_dict(self):
        return {
            "violation_id": self.violation_id,
            "session_id": self.session_id,
            "worker_id": self.worker_id,
            "violation_type": self.violation_type,
            "confidence": self.confidence_score,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "frame_number": self.frame_number,
            "bbox": [self.bbox_x1, self.bbox_y1, self.bbox_x2, self.bbox_y2],
            "snapshot_path": self.snapshot_path,
            "status": self.status,
        }
