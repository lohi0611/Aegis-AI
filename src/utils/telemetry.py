"""
AEGIS — Performance Telemetry & Timer Module
"""
import time
from typing import Dict, Any, List
import numpy as np


class PerformanceTimer:
    """High-precision latency and throughput measurement utility."""
    def __init__(self, history_len: int = 60):
        self.history_len = history_len
        self.latencies_ms: List[float] = []
        self.fps_history: List[float] = []
        self.time_history: List[str] = []
        self._t_start: float = 0.0

    def start(self) -> None:
        """Start interval timer."""
        self._t_start = time.perf_counter()

    def stop(self) -> float:
        """Stop interval timer and record latency."""
        t_end = time.perf_counter()
        elapsed_ms = (t_end - self._t_start) * 1000.0
        fps = 1000.0 / max(1e-3, elapsed_ms)

        self.latencies_ms.append(elapsed_ms)
        self.fps_history.append(fps)
        self.time_history.append(time.strftime("%H:%M:%S"))

        if len(self.latencies_ms) > self.history_len:
            self.latencies_ms.pop(0)
            self.fps_history.pop(0)
            self.time_history.pop(0)

        return elapsed_ms

    def get_stats(self) -> Dict[str, float]:
        """Compute latency and FPS statistics."""
        if not self.latencies_ms:
            return {
                "mean_fps": 0.0,
                "current_fps": 0.0,
                "mean_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
            }

        lat_arr = np.array(self.latencies_ms)
        fps_arr = np.array(self.fps_history)

        return {
            "mean_fps": round(float(np.mean(fps_arr)), 2),
            "current_fps": round(float(fps_arr[-1]), 2),
            "mean_latency_ms": round(float(np.mean(lat_arr)), 2),
            "p95_latency_ms": round(float(np.percentile(lat_arr, 95)), 2),
        }
