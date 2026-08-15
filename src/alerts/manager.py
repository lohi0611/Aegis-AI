"""
AEGIS — Alert & Event Dispatch Manager
Handles violation event throttling, cooldowns, severity routing, and notification dispatching.
"""
import time
from typing import Dict, Tuple, Optional, Any, List


class AlertManager:
    """
    Manages safety alerts and event throttling with configurable cooldown periods.
    """
    def __init__(
        self,
        cooldown_seconds: float = 15.0,
        severity_matrix: Optional[Dict[str, str]] = None,
    ):
        self.cooldown_seconds = cooldown_seconds
        self.severity_matrix = severity_matrix or {
            "NO-Hardhat": "CRITICAL",
            "NO-Safety Vest": "CRITICAL",
            "NO-Mask": "HIGH",
        }
        self.last_alert_timestamps: Dict[Tuple[str, str], float] = {}

    def should_dispatch_alert(self, worker_id: str, violation_type: str) -> bool:
        """
        Check if an alert should be dispatched or if it is currently throttled by cooldown.
        """
        key = (worker_id, violation_type)
        now = time.time()
        
        if key in self.last_alert_timestamps:
            if (now - self.last_alert_timestamps[key]) < self.cooldown_seconds:
                return False

        self.last_alert_timestamps[key] = now
        return True

    def get_severity(self, violation_type: str) -> str:
        """Resolve severity level for violation type."""
        return self.severity_matrix.get(violation_type, "HIGH")
