"""
AEGIS — Unit Tests for Utility Modules
Tests PerformanceTimer and get_logger.
"""

import logging
import time

from src.utils.logger import get_logger
from src.utils.telemetry import PerformanceTimer


class TestLogger:
    def test_get_logger_returns_logger_instance(self):
        """get_logger should return a configured Logger instance."""
        logger = get_logger("TEST_LOGGER")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "TEST_LOGGER"
        assert len(logger.handlers) >= 1

    def test_get_logger_idempotent(self):
        """Subsequent calls with same name return the same instance without duplicate handlers."""
        logger1 = get_logger("TEST_IDEMPOTENT")
        num_handlers = len(logger1.handlers)
        logger2 = get_logger("TEST_IDEMPOTENT")
        assert logger1 is logger2
        assert len(logger2.handlers) == num_handlers


class TestPerformanceTimer:
    def test_empty_timer_stats(self):
        """Empty timer returns zeroed stats."""
        timer = PerformanceTimer()
        stats = timer.get_stats()
        assert stats["mean_fps"] == 0.0
        assert stats["current_fps"] == 0.0
        assert stats["mean_latency_ms"] == 0.0
        assert stats["p95_latency_ms"] == 0.0

    def test_timer_measurement(self):
        """Timer measures elapsed latency and computes FPS."""
        timer = PerformanceTimer(history_len=10)
        timer.start()
        time.sleep(0.01)  # 10ms
        elapsed = timer.stop()
        assert elapsed >= 5.0  # At least 5ms recorded
        assert len(timer.latencies_ms) == 1
        assert len(timer.fps_history) == 1

        stats = timer.get_stats()
        assert stats["mean_fps"] > 0.0
        assert stats["mean_latency_ms"] > 0.0

    def test_history_length_cap(self):
        """Timer caps history to history_len items."""
        timer = PerformanceTimer(history_len=3)
        for _ in range(5):
            timer.start()
            time.sleep(0.001)
            timer.stop()
        assert len(timer.latencies_ms) == 3
        assert len(timer.fps_history) == 3
        assert len(timer.time_history) == 3
