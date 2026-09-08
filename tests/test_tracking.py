"""
AEGIS — Unit Tests for Centroid Tracking Module
Tests registration, distance-based association, disappearance handling, and deregistration.
"""

import pytest

from src.tracking.centroid import CentroidTracker


class TestCentroidTracker:
    def test_initial_state(self):
        """Tracker starts with no tracked objects."""
        tracker = CentroidTracker()
        assert len(tracker.objects) == 0
        assert tracker.next_id == 101

    def test_register_single_object(self):
        """Registering a new object assigns track ID prefix and increments next_id."""
        tracker = CentroidTracker(track_id_prefix="WKR_")
        track_id = tracker.register((50, 50), "person", [0, 0, 100, 100])
        assert track_id == "WKR_101"
        assert tracker.objects[track_id] == (50, 50)
        assert tracker.classes[track_id] == "person"
        assert tracker.bboxes[track_id] == [0, 0, 100, 100]
        assert tracker.disappeared[track_id] == 0

    def test_update_initial_detections(self):
        """First update registers all input detections."""
        tracker = CentroidTracker()
        rects = [[0, 0, 100, 100], [200, 200, 300, 300]]
        classes = ["person", "person"]
        ids = tracker.update(rects, classes)
        assert len(ids) == 2
        assert ids[0] == "WKR_101"
        assert ids[1] == "WKR_102"
        assert len(tracker.objects) == 2

    def test_update_tracking_continuity(self):
        """Slight motion updates centroid without changing ID."""
        tracker = CentroidTracker(min_distance=100.0)
        tracker.update([[10, 10, 110, 110]], ["person"])
        # Slight movement: from (60, 60) to (65, 65), dist ~7.07 < 100
        ids = tracker.update([[15, 15, 115, 115]], ["person"])
        assert ids == ["WKR_101"]
        assert tracker.objects["WKR_101"] == (65, 65)

    def test_update_class_mismatch_creates_new_id(self):
        """Object with different class is not matched even if close."""
        tracker = CentroidTracker()
        tracker.update([[10, 10, 110, 110]], ["person"])
        ids = tracker.update([[12, 12, 112, 112]], ["vehicle"])
        assert ids == ["WKR_102"]

    def test_update_empty_rects_increments_disappeared(self):
        """Empty detections increment disappeared counter."""
        tracker = CentroidTracker(max_disappeared=2)
        tracker.update([[10, 10, 110, 110]], ["person"])
        assert tracker.disappeared["WKR_101"] == 0

        # Disappeared frame 1
        ids = tracker.update([], [])
        assert ids == []
        assert tracker.disappeared["WKR_101"] == 1

        # Disappeared frame 2
        tracker.update([], [])
        assert tracker.disappeared["WKR_101"] == 2

        # Disappeared frame 3 > max_disappeared (2) -> deregistered
        tracker.update([], [])
        assert "WKR_101" not in tracker.objects

    def test_deregister_removes_all_state(self):
        """Deregistration clears all internal dictionaries."""
        tracker = CentroidTracker()
        w_id = tracker.register((50, 50), "person", [0, 0, 100, 100])
        tracker.deregister(w_id)
        assert w_id not in tracker.objects
        assert w_id not in tracker.disappeared
        assert w_id not in tracker.classes
        assert w_id not in tracker.bboxes
