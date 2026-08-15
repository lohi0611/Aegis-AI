"""
AEGIS — Unit Tests for Spatial PPE Association Module
Tests geometric containment, IoU, and anatomical scoring logic.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.association.spatial import (
    compute_bbox_area,
    compute_intersection_area,
    compute_containment_ratio,
    compute_iou,
    compute_anatomical_score,
    SpatialPPEAssociator,
)


class TestBboxUtils:
    def test_compute_bbox_area_valid(self):
        assert compute_bbox_area([0, 0, 10, 20]) == pytest.approx(200.0)

    def test_compute_bbox_area_zero(self):
        assert compute_bbox_area([5, 5, 5, 5]) == pytest.approx(0.0)

    def test_intersection_full_overlap(self):
        box = [0, 0, 10, 10]
        assert compute_intersection_area(box, box) == pytest.approx(100.0)

    def test_intersection_no_overlap(self):
        assert compute_intersection_area([0, 0, 5, 5], [10, 10, 20, 20]) == pytest.approx(0.0)

    def test_containment_fully_inside(self):
        """Small PPE box fully inside large person box."""
        ppe_box = [2, 2, 8, 8]
        person_box = [0, 0, 10, 10]
        ratio = compute_containment_ratio(ppe_box, person_box)
        assert ratio == pytest.approx(1.0)

    def test_containment_no_overlap(self):
        ratio = compute_containment_ratio([20, 20, 30, 30], [0, 0, 10, 10])
        assert ratio == pytest.approx(0.0)

    def test_iou_identical_boxes(self):
        box = [0, 0, 10, 10]
        assert compute_iou(box, box) == pytest.approx(1.0)

    def test_iou_no_overlap(self):
        assert compute_iou([0, 0, 5, 5], [10, 10, 20, 20]) == pytest.approx(0.0)

    def test_iou_partial_overlap(self):
        iou = compute_iou([0, 0, 10, 10], [5, 5, 15, 15])
        # Intersection = 5x5=25, Union = 100+100-25=175
        assert iou == pytest.approx(25.0 / 175.0, abs=1e-3)


class TestAnatomicalScore:
    def test_hardhat_in_head_region(self):
        # PPE center at y=150, person from y=100 to y=400 -> rel_y = 50/300 = 0.167 (head)
        score = compute_anatomical_score("Hardhat", [40, 130, 80, 170], [20, 100, 100, 400])
        assert score == pytest.approx(1.0)

    def test_hardhat_in_foot_region(self):
        # PPE center near feet of person
        score = compute_anatomical_score("Hardhat", [40, 370, 80, 400], [20, 100, 100, 400])
        assert score == pytest.approx(0.1)

    def test_safety_vest_in_torso_region(self):
        # PPE center at y=250, person from y=100 to y=400 -> rel_y = 150/300 = 0.5 (torso)
        score = compute_anatomical_score("Safety Vest", [40, 230, 80, 270], [20, 100, 100, 400])
        assert score == pytest.approx(1.0)


class TestSpatialAssociator:
    def setup_method(self):
        self.associator = SpatialPPEAssociator(containment_threshold=0.3)

    def test_associate_hardhat_to_person(self):
        """Hardhat box contained inside person box should be assigned."""
        person_dets = [{"bbox": [0, 0, 100, 300], "track_id": "WKR_101", "confidence": 0.9}]
        ppe_dets = [{"class_name": "Hardhat", "bbox": [5, 5, 60, 60], "confidence": 0.85}]
        workers, isolated = self.associator.associate(person_dets, ppe_dets)
        assert len(workers) == 1
        assert len(workers[0]["assigned_ppe"]) == 1
        assert workers[0]["assigned_ppe"][0]["class_name"] == "Hardhat"
        assert len(isolated) == 0

    def test_no_person_returns_isolated(self):
        """If no person detected, all PPE should be isolated."""
        ppe_dets = [{"class_name": "NO-Hardhat", "bbox": [10, 10, 50, 50], "confidence": 0.75}]
        workers, isolated = self.associator.associate([], ppe_dets)
        assert len(workers) == 0
        assert len(isolated) == 1

    def test_out_of_range_ppe_not_assigned(self):
        """PPE far from person should not be assigned."""
        person_dets = [{"bbox": [0, 0, 100, 100], "track_id": "WKR_101", "confidence": 0.9}]
        ppe_dets = [{"class_name": "Hardhat", "bbox": [200, 200, 300, 300], "confidence": 0.8}]
        workers, isolated = self.associator.associate(person_dets, ppe_dets)
        assert len(workers[0]["assigned_ppe"]) == 0
        assert len(isolated) == 1
