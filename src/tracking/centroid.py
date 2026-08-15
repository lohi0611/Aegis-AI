"""
AEGIS — Centroid Tracking Module
Maintains persistent worker identities across video frames using Euclidean centroid association.
"""
from typing import List, Dict, Tuple, Optional
import numpy as np


class CentroidTracker:
    """
    Centroid tracker assigning stable worker IDs across sequential video frames.
    """
    def __init__(
        self,
        max_disappeared: int = 15,
        min_distance: float = 100.0,
        track_id_prefix: str = "WKR_",
    ):
        self.next_id = 101
        self.objects: Dict[str, Tuple[int, int]] = {}
        self.disappeared: Dict[str, int] = {}
        self.classes: Dict[str, str] = {}
        self.bboxes: Dict[str, List[int]] = {}
        self.logged_violations: Dict[Tuple[str, str], float] = {}

        self.max_disappeared = max_disappeared
        self.min_distance = min_distance
        self.prefix = track_id_prefix

    def register(self, centroid: Tuple[int, int], class_name: str, bbox: List[int]) -> str:
        """Register a new object track."""
        w_id = f"{self.prefix}{self.next_id}"
        self.objects[w_id] = centroid
        self.disappeared[w_id] = 0
        self.classes[w_id] = class_name
        self.bboxes[w_id] = bbox
        self.next_id += 1
        return w_id

    def deregister(self, w_id: str) -> None:
        """Deregister an object track."""
        for d in (self.objects, self.disappeared, self.classes, self.bboxes):
            d.pop(w_id, None)

    def update(self, rects: List[List[int]], class_names: List[str]) -> List[str]:
        """
        Update object tracks based on input bounding boxes.
        
        Args:
            rects: List of [x1, y1, x2, y2]
            class_names: List of class name strings aligned with rects
            
        Returns:
            List of track IDs assigned to each input box.
        """
        if len(rects) == 0:
            for w_id in list(self.disappeared.keys()):
                self.disappeared[w_id] += 1
                if self.disappeared[w_id] > self.max_disappeared:
                    self.deregister(w_id)
            return []

        input_centroids = [
            ((int(r[0]) + int(r[2])) // 2, (int(r[1]) + int(r[3])) // 2)
            for r in rects
        ]

        if len(self.objects) == 0:
            return [
                self.register(c, cn, r)
                for c, cn, r in zip(input_centroids, class_names, rects)
            ]

        obj_ids = list(self.objects.keys())
        obj_centroids = list(self.objects.values())
        assigned_ids: List[Optional[str]] = [None] * len(input_centroids)
        used_objs = set()

        for i, (icx, icy) in enumerate(input_centroids):
            best_dist = float("inf")
            best_id = None
            for j, w_id in enumerate(obj_ids):
                if w_id in used_objs or self.classes.get(w_id) != class_names[i]:
                    continue
                ocx, ocy = obj_centroids[j]
                dist = ((icx - ocx) ** 2 + (icy - ocy) ** 2) ** 0.5
                if dist < best_dist and dist < self.min_distance:
                    best_dist = dist
                    best_id = w_id

            if best_id is not None:
                self.objects[best_id] = (icx, icy)
                self.bboxes[best_id] = rects[i]
                self.disappeared[best_id] = 0
                assigned_ids[i] = best_id
                used_objs.add(best_id)
            else:
                assigned_ids[i] = self.register((icx, icy), class_names[i], rects[i])

        for w_id in obj_ids:
            if w_id not in used_objs:
                self.disappeared[w_id] += 1
                if self.disappeared[w_id] > self.max_disappeared:
                    self.deregister(w_id)

        return [aid if aid else "Unknown" for aid in assigned_ids]
