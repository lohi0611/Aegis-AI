"""
AEGIS — Unit Tests for PPE Compliance Rule Engine
Tests violation classification, compliant status, missing PPE detection.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.compliance.rules import PPERuleEngine
from src.compliance.temporal import TemporalHysteresisFilter
from src.compliance.engine import ComplianceEngine


class TestPPERuleEngine:
    def setup_method(self):
        self.engine = PPERuleEngine(
            require_hardhat=True,
            require_vest=True,
            require_mask=False,
        )

    def _make_worker(self, ppe_classes):
        return {
            "track_id": "WKR_101",
            "bbox": [0, 0, 100, 300],
            "confidence": 0.85,
            "assigned_ppe": [{"class_name": c, "confidence": 0.80, "bbox": [0, 0, 50, 50]} for c in ppe_classes],
        }

    def test_fully_compliant(self):
        worker = self._make_worker(["Hardhat", "Safety Vest"])
        result = self.engine.evaluate_worker(worker)
        assert result["is_compliant"] is True
        assert result["status"] == "Compliant"
        assert len(result["violations"]) == 0

    def test_no_hardhat_explicit(self):
        worker = self._make_worker(["NO-Hardhat", "Safety Vest"])
        result = self.engine.evaluate_worker(worker)
        assert result["is_compliant"] is False
        assert "NO-Hardhat" in result["violations"]

    def test_no_vest_explicit(self):
        worker = self._make_worker(["Hardhat", "NO-Safety Vest"])
        result = self.engine.evaluate_worker(worker)
        assert result["is_compliant"] is False
        assert "NO-Safety Vest" in result["violations"]

    def test_both_violations(self):
        worker = self._make_worker(["NO-Hardhat", "NO-Safety Vest"])
        result = self.engine.evaluate_worker(worker)
        assert result["is_compliant"] is False
        assert len(result["violations"]) == 2

    def test_mask_optional_no_violation_when_disabled(self):
        worker = self._make_worker(["Hardhat", "Safety Vest", "NO-Mask"])
        result = self.engine.evaluate_worker(worker)
        # Mask is not required, NO-Mask should not trigger violation
        assert result["is_compliant"] is True

    def test_mask_required_violation(self):
        engine_with_mask = PPERuleEngine(require_hardhat=True, require_vest=True, require_mask=True)
        worker = self._make_worker(["Hardhat", "Safety Vest", "NO-Mask"])
        result = engine_with_mask.evaluate_worker(worker)
        assert result["is_compliant"] is False
        assert "NO-Mask" in result["violations"]

    def test_empty_ppe_all_required_missing(self):
        """If person detected with no PPE at all, expect violations for missing required items."""
        worker = self._make_worker([])
        result = self.engine.evaluate_worker(worker)
        assert result["is_compliant"] is False
        assert len(result["violations"]) == 2  # Hardhat + Vest


class TestTemporalHysteresisFilter:
    def test_single_frame_not_confirmed(self):
        """Single frame violation should NOT be confirmed (N=3)."""
        filt = TemporalHysteresisFilter(violation_confirm_frames=3, resolution_confirm_frames=5)
        workers_frame1 = [{
            "worker_id": "WKR_101",
            "violations": ["NO-Hardhat"],
            "is_compliant": False,
            "status": "Violation",
            "bbox": [],
            "confidence": 0.8,
            "detected_ppe": [],
            "missing_ppe": [],
            "confirmed_violations": [],
        }]
        result = filt.update(workers_frame1)
        # After 1 frame, should NOT be confirmed (need 3)
        assert result[0]["temporally_confirmed"] is False

    def test_three_consecutive_frames_confirmed(self):
        """After 3 consecutive violation frames, violation should be confirmed."""
        filt = TemporalHysteresisFilter(violation_confirm_frames=3, resolution_confirm_frames=5)
        viol_worker = [{
            "worker_id": "WKR_101",
            "violations": ["NO-Hardhat"],
            "is_compliant": False,
            "status": "Violation",
            "bbox": [],
            "confidence": 0.8,
            "detected_ppe": [],
            "missing_ppe": [],
            "confirmed_violations": [],
        }]
        for _ in range(3):
            result = filt.update(viol_worker)
        assert result[0]["temporally_confirmed"] is True

    def test_resolution_after_clean_frames(self):
        """After M clean frames, confirmed violation should resolve."""
        filt = TemporalHysteresisFilter(violation_confirm_frames=2, resolution_confirm_frames=3)
        viol_worker = [{
            "worker_id": "WKR_101",
            "violations": ["NO-Hardhat"],
            "is_compliant": False,
            "status": "Violation",
            "bbox": [],
            "confidence": 0.8,
            "detected_ppe": [],
            "missing_ppe": [],
            "confirmed_violations": [],
        }]
        clean_worker = [{
            "worker_id": "WKR_101",
            "violations": [],
            "is_compliant": True,
            "status": "Compliant",
            "bbox": [],
            "confidence": 0.8,
            "detected_ppe": ["Hardhat"],
            "missing_ppe": [],
            "confirmed_violations": [],
        }]
        for _ in range(2):
            filt.update(viol_worker)
        for _ in range(3):
            result = filt.update(clean_worker)
        assert result[0]["temporally_confirmed"] is False


class TestComplianceEngine:
    def test_no_persons_detected(self):
        """When no persons detected, output should have no workers and no violations."""
        engine = ComplianceEngine(require_hardhat=True, require_vest=True)
        detections = [{"class_name": "Safety Cone", "bbox": [10, 10, 50, 50], "confidence": 0.75}]
        result = engine.process_frame_detections(detections)
        assert len(result["workers"]) == 0
        assert result["site_has_violation"] is False

    def test_full_pipeline_violation(self):
        """Full pipeline should detect NO-Hardhat as violation."""
        engine = ComplianceEngine(require_hardhat=True, require_vest=False, violation_confirm_frames=1)
        detections = [
            {"class_name": "Person", "bbox": [0, 0, 100, 300], "confidence": 0.9},
            {"class_name": "NO-Hardhat", "bbox": [10, 5, 90, 80], "confidence": 0.85},
        ]
        result = engine.process_frame_detections(detections)
        # After 1 frame with confirm_frames=1, should detect violation
        assert result["total_active_violations"] > 0
