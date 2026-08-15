"""
AEGIS — Temporal Hysteresis Filter
Suppresses single-frame detector flicker and transient occlusion.
Requires N consecutive frames to confirm a violation event, and M frames to resolve it.
"""
from typing import Dict, Any, List, Set, Optional


class TemporalHysteresisFilter:
    """
    Stateful temporal confirmation filter for worker safety violations.
    """
    def __init__(
        self,
        violation_confirm_frames: int = 3,
        resolution_confirm_frames: int = 5,
    ):
        self.violation_confirm_frames = violation_confirm_frames
        self.resolution_confirm_frames = resolution_confirm_frames

        # State tracking: worker_id -> { 'consecutive_violations': int, 'consecutive_clean': int, 'confirmed_violations': Set[str] }
        self.worker_states: Dict[str, Dict[str, Any]] = {}

    def update(self, evaluated_workers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process worker compliance states through the temporal hysteresis window.
        
        Args:
            evaluated_workers: Output from PPERuleEngine.evaluate_worker
            
        Returns:
            List of stabilized worker records with 'temporally_confirmed' flag.
        """
        current_seen_ids = set()
        stabilized_records = []

        for w in evaluated_workers:
            w_id = w["worker_id"]
            current_seen_ids.add(w_id)

            if w_id not in self.worker_states:
                self.worker_states[w_id] = {
                    "consecutive_violations": 0,
                    "consecutive_clean": 0,
                    "confirmed_violations": set(),
                }

            state = self.worker_states[w_id]
            instant_violations = set(w.get("violations", []))

            if len(instant_violations) > 0:
                state["consecutive_violations"] += 1
                state["consecutive_clean"] = 0
                
                # Check confirmation threshold
                if state["consecutive_violations"] >= self.violation_confirm_frames:
                    state["confirmed_violations"] = instant_violations
            else:
                state["consecutive_clean"] += 1
                
                # Check resolution threshold
                if state["consecutive_clean"] >= self.resolution_confirm_frames:
                    state["confirmed_violations"] = set()
                    state["consecutive_violations"] = 0

            # Formulate stabilized record
            is_confirmed_violation = len(state["confirmed_violations"]) > 0
            
            w_copy = dict(w)
            w_copy["temporally_confirmed"] = is_confirmed_violation
            w_copy["confirmed_violations"] = sorted(list(state["confirmed_violations"]))
            w_copy["temporal_state"] = {
                "consecutive_violations": state["consecutive_violations"],
                "consecutive_clean": state["consecutive_clean"],
            }
            
            # If confirmed violation, update status
            if is_confirmed_violation:
                w_copy["status"] = "Violation"
                w_copy["is_compliant"] = False
                w_copy["violations"] = sorted(list(state["confirmed_violations"]))
            elif state["consecutive_violations"] > 0:
                # Candidate under confirmation window
                w_copy["status"] = "Pending Confirmation"
            else:
                w_copy["status"] = "Compliant"
                w_copy["is_compliant"] = True

            stabilized_records.append(w_copy)

        # Cleanup old workers not seen for 60 frames
        for wid in list(self.worker_states.keys()):
            if wid not in current_seen_ids:
                self.worker_states[wid]["consecutive_clean"] += 1
                if self.worker_states[wid]["consecutive_clean"] > 60:
                    del self.worker_states[wid]

        return stabilized_records
