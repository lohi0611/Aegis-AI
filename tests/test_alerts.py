"""
AEGIS — Unit Tests for Alert Manager
Tests cooldown throttling, severity resolution, and deduplication logic.
"""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.alerts.manager import AlertManager


class TestAlertManager:
    def setup_method(self):
        self.manager = AlertManager(cooldown_seconds=1.0)

    def test_first_alert_dispatched(self):
        """First alert for a new worker+violation pair should be dispatched."""
        assert self.manager.should_dispatch_alert("WKR_101", "NO-Hardhat") is True

    def test_duplicate_within_cooldown_suppressed(self):
        """Duplicate alert within cooldown period should be suppressed."""
        self.manager.should_dispatch_alert("WKR_101", "NO-Hardhat")
        # Immediately try again — should be throttled
        assert self.manager.should_dispatch_alert("WKR_101", "NO-Hardhat") is False

    def test_different_worker_same_violation_dispatched(self):
        """Different workers with same violation should each be dispatched."""
        self.manager.should_dispatch_alert("WKR_101", "NO-Hardhat")
        assert self.manager.should_dispatch_alert("WKR_102", "NO-Hardhat") is True

    def test_after_cooldown_alert_dispatched_again(self):
        """After cooldown expires, the same pair should be dispatchable again."""
        manager = AlertManager(cooldown_seconds=0.05)
        manager.should_dispatch_alert("WKR_101", "NO-Hardhat")
        time.sleep(0.1)
        assert manager.should_dispatch_alert("WKR_101", "NO-Hardhat") is True

    def test_severity_critical(self):
        assert self.manager.get_severity("NO-Hardhat") == "CRITICAL"
        assert self.manager.get_severity("NO-Safety Vest") == "CRITICAL"

    def test_severity_high(self):
        assert self.manager.get_severity("NO-Mask") == "HIGH"

    def test_severity_unknown_defaults_high(self):
        assert self.manager.get_severity("Unknown-Violation") == "HIGH"
