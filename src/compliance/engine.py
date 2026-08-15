"""
AEGIS — Unified PPE Compliance & Safety Decision Engine
Coordinates spatial association, rule evaluation, and temporal hysteresis.
"""
from typing import List, Dict, Any, Tuple, Optional
from src.association.spatial import SpatialPPEAssociator
from src.compliance.rules import PPERuleEngine
from src.compliance.temporal import TemporalHysteresisFilter


class ComplianceEngine:
    """
    Unified Safety Compliance Engine for worker-level PPE decision making.
    """
    def __init__(
        self,
        require_hardhat: bool = True,
        require_vest: bool = True,
        require_mask: bool = False,
        violation_confirm_frames: int = 3,
        resolution_confirm_frames: int = 5,
        containment_threshold: float = 0.35,
    ):
        self.associator = SpatialPPEAssociator(containment_threshold=containment_threshold)
        self.rule_engine = PPERuleEngine(
            require_hardhat=require_hardhat,
            require_vest=require_vest,
            require_mask=require_mask,
        )
        self.temporal_filter = TemporalHysteresisFilter(
            violation_confirm_frames=violation_confirm_frames,
            resolution_confirm_frames=resolution_confirm_frames,
        )

    def process_frame_detections(
        self,
        detections: List[Dict[str, Any]],
        person_track_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Process all detections in a frame and output structured worker compliance reports.
        
        Args:
            detections: List of dicts from YOLOv8 detector with 'class_name', 'bbox', 'confidence'.
            person_track_ids: Optional list of tracker IDs aligned with Person detections.
            
        Returns:
            Dict containing:
              - 'workers': List of worker-level compliance records.
              - 'isolated_ppe': List of unassociated PPE detections.
              - 'site_has_violation': Boolean indicating overall site hazard status.
              - 'total_active_violations': Total count of confirmed violations.
        """
        person_dets = []
        ppe_dets = []

        person_idx = 0
        for d in detections:
            cname = d["class_name"]
            if cname == "Person":
                track_id = (
                    person_track_ids[person_idx]
                    if person_track_ids and person_idx < len(person_track_ids) and person_track_ids[person_idx]
                    else f"WKR_{100 + person_idx}"
                )
                person_idx += 1
                person_dets.append({
                    "bbox": d["bbox"],
                    "track_id": track_id,
                    "confidence": d.get("confidence", 1.0),
                })
            else:
                ppe_dets.append(d)

        # 1. Spatial Association
        associated_workers, isolated_ppe = self.associator.associate(person_dets, ppe_dets)

        # 2. Rule Evaluation
        evaluated_workers = [self.rule_engine.evaluate_worker(w) for w in associated_workers]

        # 3. Temporal Stability Hysteresis
        stabilized_workers = self.temporal_filter.update(evaluated_workers)

        # 4. Check for standalone unassociated negative classes (e.g. isolated NO-Hardhat)
        standalone_violations = [p for p in isolated_ppe if p["class_name"] in {"NO-Hardhat", "NO-Safety Vest", "NO-Mask"}]

        confirmed_worker_violations = sum(1 for w in stabilized_workers if w["status"] == "Violation")
        total_violations = confirmed_worker_violations + len(standalone_violations)
        site_has_violation = total_violations > 0

        return {
            "workers": stabilized_workers,
            "isolated_ppe": isolated_ppe,
            "standalone_violations": standalone_violations,
            "total_active_violations": total_violations,
            "site_has_violation": site_has_violation,
        }
