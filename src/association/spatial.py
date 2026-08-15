"""
AEGIS — Person-to-PPE Spatial Association Engine
Associates detected PPE items (Hardhat, Mask, Vest, NO-Hardhat, NO-Mask, NO-Safety Vest)
with individual detected workers based on geometric containment, IoU overlap, and anatomical alignment.
"""
from typing import List, Dict, Any, Tuple, Optional
import numpy as np


def compute_bbox_area(box: List[float]) -> float:
    """Compute area of bounding box [x1, y1, x2, y2]."""
    w = max(0.0, box[2] - box[0])
    h = max(0.0, box[3] - box[1])
    return w * h


def compute_intersection_area(boxA: List[float], boxB: List[float]) -> float:
    """Compute intersection area between two bounding boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    inter_w = max(0.0, xB - xA)
    inter_h = max(0.0, yB - yA)
    return inter_w * inter_h


def compute_containment_ratio(ppe_box: List[float], person_box: List[float]) -> float:
    """
    Compute fraction of the PPE bounding box contained inside the Person bounding box.
    Returns value in [0.0, 1.0].
    """
    ppe_area = compute_bbox_area(ppe_box)
    if ppe_area <= 0.0:
        return 0.0
    inter_area = compute_intersection_area(ppe_box, person_box)
    return inter_area / ppe_area


def compute_iou(boxA: List[float], boxB: List[float]) -> float:
    """Compute Intersection-over-Union between two bounding boxes."""
    areaA = compute_bbox_area(boxA)
    areaB = compute_bbox_area(boxB)
    inter_area = compute_intersection_area(boxA, boxB)
    union_area = areaA + areaB - inter_area
    if union_area <= 0.0:
        return 0.0
    return inter_area / union_area


def compute_anatomical_score(ppe_class: str, ppe_box: List[float], person_box: List[float]) -> float:
    """
    Check if PPE center vertically aligns with human anatomy within the person bounding box.
    - Head equipment (Hardhat, NO-Hardhat, Mask, NO-Mask): expected in upper 45% of height.
    - Torso equipment (Safety Vest, NO-Safety Vest): expected in upper 20%-85% of height.
    """
    person_h = person_box[3] - person_box[1]
    if person_h <= 0.0:
        return 0.5
    
    ppe_cy = (ppe_box[1] + ppe_box[3]) / 2.0
    rel_y = (ppe_cy - person_box[1]) / person_h  # 0.0 = top of head, 1.0 = feet

    head_classes = {"Hardhat", "NO-Hardhat", "Mask", "NO-Mask"}
    torso_classes = {"Safety Vest", "NO-Safety Vest"}

    if ppe_class in head_classes:
        # Highest score if in top 40% of body
        if 0.0 <= rel_y <= 0.45:
            return 1.0
        elif rel_y < 0.65:
            return 0.5
        return 0.1

    if ppe_class in torso_classes:
        # Highest score if in torso region (15% to 80% of body)
        if 0.15 <= rel_y <= 0.85:
            return 1.0
        return 0.3

    return 0.5


class SpatialPPEAssociator:
    """
    Associates object-level PPE detections to worker detections.
    """
    def __init__(
        self,
        containment_threshold: float = 0.35,
        containment_weight: float = 0.60,
        iou_weight: float = 0.20,
        anatomical_weight: float = 0.20,
    ):
        self.containment_threshold = containment_threshold
        self.containment_weight = containment_weight
        self.iou_weight = iou_weight
        self.anatomical_weight = anatomical_weight

    def associate(
        self,
        person_detections: List[Dict[str, Any]],
        ppe_detections: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Associate PPE detections to person detections.
        
        Args:
            person_detections: List of dicts with keys 'bbox', 'track_id', 'confidence'
            ppe_detections: List of dicts with keys 'class_name', 'bbox', 'confidence'
            
        Returns:
            Tuple of:
              1. List of worker dicts, each with attached 'assigned_ppe' list.
              2. List of unassigned/isolated PPE detections.
        """
        # Deep clone person records
        workers = []
        for p in person_detections:
            workers.append({
                "track_id": p.get("track_id", "Unknown"),
                "bbox": p["bbox"],
                "confidence": p.get("confidence", 1.0),
                "assigned_ppe": [],
            })

        unassigned_ppe = []

        if not workers:
            # If no person detected, all PPE is unassigned
            return [], ppe_detections

        for ppe in ppe_detections:
            ppe_box = ppe["bbox"]
            ppe_cls = ppe["class_name"]
            
            best_worker_idx = -1
            best_score = -1.0

            for idx, worker in enumerate(workers):
                person_box = worker["bbox"]
                containment = compute_containment_ratio(ppe_box, person_box)
                
                if containment >= self.containment_threshold:
                    iou = compute_iou(ppe_box, person_box)
                    anat = compute_anatomical_score(ppe_cls, ppe_box, person_box)
                    score = (
                        self.containment_weight * containment +
                        self.iou_weight * iou +
                        self.anatomical_weight * anat
                    )
                    if score > best_score:
                        best_score = score
                        best_worker_idx = idx

            if best_worker_idx >= 0:
                workers[best_worker_idx]["assigned_ppe"].append(ppe)
            else:
                unassigned_ppe.append(ppe)

        return workers, unassigned_ppe
