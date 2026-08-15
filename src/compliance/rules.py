"""
AEGIS — PPE Compliance Rule Definitions
Evaluates worker PPE states against site safety policies.
"""
from typing import List, Dict, Any, Set, Tuple


class PPERuleEngine:
    """
    Formal rule engine evaluating worker compliance based on detected and negative PPE classes.
    """
    def __init__(
        self,
        require_hardhat: bool = True,
        require_vest: bool = True,
        require_mask: bool = False,
    ):
        self.require_hardhat = require_hardhat
        self.require_vest = require_vest
        self.require_mask = require_mask

    def evaluate_worker(self, worker_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate compliance for a single worker with associated PPE detections.
        
        Args:
            worker_record: Dict containing 'track_id', 'bbox', 'assigned_ppe', 'confidence'
            
        Returns:
            Dict containing worker compliance evaluation status.
        """
        assigned_ppe = worker_record.get("assigned_ppe", [])
        ppe_classes = {p["class_name"] for p in assigned_ppe}
        
        violations: List[str] = []
        detected_ppe: List[str] = []
        missing_ppe: List[str] = []
        
        # 1. Hardhat Rule
        if "NO-Hardhat" in ppe_classes:
            violations.append("NO-Hardhat")
        elif "Hardhat" in ppe_classes:
            detected_ppe.append("Hardhat")
        elif self.require_hardhat:
            # Person detected but no hardhat found on head
            missing_ppe.append("Hardhat")
            violations.append("NO-Hardhat")

        # 2. Safety Vest Rule
        if "NO-Safety Vest" in ppe_classes:
            violations.append("NO-Safety Vest")
        elif "Safety Vest" in ppe_classes:
            detected_ppe.append("Safety Vest")
        elif self.require_vest:
            missing_ppe.append("Safety Vest")
            violations.append("NO-Safety Vest")

        # 3. Mask Rule (if enabled)
        if "NO-Mask" in ppe_classes:
            if self.require_mask:
                violations.append("NO-Mask")
        elif "Mask" in ppe_classes:
            detected_ppe.append("Mask")
        elif self.require_mask:
            missing_ppe.append("Mask")
            violations.append("NO-Mask")

        is_compliant = len(violations) == 0

        # Compute aggregate confidence
        confidences = [p.get("confidence", 0.5) for p in assigned_ppe]
        confidences.append(worker_record.get("confidence", 0.8))
        avg_conf = float(sum(confidences) / len(confidences)) if confidences else 0.8

        return {
            "worker_id": worker_record.get("track_id", "Unknown"),
            "bbox": worker_record.get("bbox", []),
            "is_compliant": is_compliant,
            "violations": violations,
            "detected_ppe": detected_ppe,
            "missing_ppe": missing_ppe,
            "confidence": round(avg_conf, 2),
            "status": "Compliant" if is_compliant else "Violation",
        }
