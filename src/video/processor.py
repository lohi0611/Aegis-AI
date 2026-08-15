"""
AEGIS — Robust Video Stream Processor
Handles video capture, frame decimation, resolution clamping, error recovery, and FPS telemetry.
"""
import os
import time
from typing import Optional, Generator, Tuple, Union
from pathlib import Path
import cv2
import numpy as np


class VideoStreamProcessor:
    """
    Manages robust video stream capture and preprocessing with memory protection.
    """
    def __init__(
        self,
        source: Union[int, str],
        process_every_n_frames: int = 1,
        max_resolution: Tuple[int, int] = (1280, 720),
        use_dshow: bool = True,
    ):
        self.source = source
        self.process_every_n_frames = max(1, process_every_n_frames)
        self.max_resolution = max_resolution
        self.use_dshow = use_dshow
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame_count = 0
        self.processed_count = 0
        self.is_opened = False

        self._init_capture()

    def _init_capture(self) -> bool:
        """Initialize OpenCV VideoCapture."""
        if isinstance(self.source, int) and self.use_dshow and os.name == "nt":
            self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(self.source)

        self.is_opened = self.cap.isOpened()
        return self.is_opened

    def frames(self) -> Generator[Tuple[int, np.ndarray, np.ndarray], None, None]:
        """
        Yields (frame_idx, rgb_frame, bgr_raw_frame) with frame skipping.
        """
        if not self.cap or not self.cap.isOpened():
            return

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret or frame is None:
                break

            self.frame_count += 1

            if self.frame_count % self.process_every_n_frames != 0:
                continue

            self.processed_count += 1

            # Clamp resolution if needed
            h, w = frame.shape[:2]
            max_w, max_h = self.max_resolution
            if w > max_w or h > max_h:
                scale = min(max_w / w, max_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield self.frame_count, rgb_frame, frame

    def release(self) -> None:
        """Safely release capture resources."""
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.is_opened = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
