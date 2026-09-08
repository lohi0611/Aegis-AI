import os
import sys
import tempfile
import numpy as np

# Safe ultralytics import (may fail on headless Linux without libGL or GPU packages)
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except Exception as _yolo_err:
    YOLO = None
    YOLO_AVAILABLE = False
    print(f"[AEGIS] Ultralytics/YOLO import failed: {_yolo_err}")


class PPEDetector:
    def __init__(self, model_path=None, conf=0.5):
        self.conf = conf
        self.class_names = [
            "Hardhat",
            "Mask",
            "NO-Hardhat",
            "NO-Mask",
            "NO-Safety Vest",
            "Person",
            "Safety Cone",
            "Safety Vest",
            "Machinery",
            "Vehicle"
        ]
        self.is_fallback = False
        self.model = None

        if not YOLO_AVAILABLE:
            print("[AEGIS] Operating in simulation / fallback detector mode (Ultralytics not installed or missing shared libraries).")
            self.is_fallback = True
            return

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)

        # On Streamlit Cloud the repo is mounted read-only; store downloaded models in /tmp
        is_cloud = (
            os.environ.get("STREAMLIT_SHARING_MODE") == "1"
            or os.environ.get("HOME", "").startswith("/home/adminuser")
        )
        if is_cloud:
            models_dir = os.path.join(tempfile.gettempdir(), "aegis_models")
        else:
            models_dir = os.path.join(project_root, "models")

        try:
            os.makedirs(models_dir, exist_ok=True)
        except OSError:
            models_dir = tempfile.gettempdir()

        if model_path is None:
            potential_paths = [
                os.path.join(models_dir, "yolov8_ppe.pt"),
                os.path.join(project_root, "models", "yolov8_ppe.pt"),
                os.path.join(current_dir, "models", "yolov8_ppe.pt"),
                "models/yolov8_ppe.pt"
            ]

            for p in potential_paths:
                if os.path.exists(p):
                    model_path = p
                    break

            if model_path is None or not os.path.exists(model_path):
                model_target = os.path.join(models_dir, "yolov8_ppe.pt")
                if not os.path.exists(model_target):
                    try:
                        import gdown
                        model_url = "https://drive.google.com/uc?id=1qLB4ZjijrpNdHcphQftVudm8y4SOZDoL"
                        gdown.download(model_url, model_target, quiet=False)
                    except Exception as _e:
                        print(f"[AEGIS] Model download failed: {_e}")

                if os.path.exists(model_target):
                    model_path = model_target
                else:
                    # Point fallback to writable models dir
                    model_path = os.path.join(models_dir, "yolov8n.pt")

        try:
            self.model = YOLO(model_path)
            print(f"[AEGIS] PPEDetector successfully initialized with model: {model_path}")
        except Exception as _load_err:
            print(f"[AEGIS] Failed to instantiate YOLO model ({_load_err}). Falling back to simulation detector.")
            self.is_fallback = True
            self.model = None

    def detect(self, frame, line_width=2, alert_classes=None):
        if self.is_fallback or self.model is None:
            return self._fallback_detect(frame, alert_classes=alert_classes)

        try:
            results = self.model.predict(frame, conf=self.conf, verbose=False)
            if line_width is not None:
                annotated = results[0].plot(line_width=line_width, labels=True, conf=True)
            else:
                annotated = results[0].plot(labels=True, conf=True)

            detections = []
            boxes = results[0].boxes

            for box in boxes:
                cls_idx = int(box.cls[0])
                class_name = self.model.names[cls_idx]

                if alert_classes and class_name not in alert_classes:
                    continue

                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append({
                    "class_name": class_name,
                    "confidence": round(conf, 2),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)]
                })

            return annotated, detections
        except Exception as _pred_err:
            print(f"[AEGIS] Prediction error: {_pred_err}")
            return self._fallback_detect(frame, alert_classes=alert_classes)

    def _fallback_detect(self, frame, alert_classes=None):
        """Simulation detector when neural network weights or GPU libraries are unavailable."""
        h, w = frame.shape[:2] if hasattr(frame, "shape") else (480, 640)
        detections = []

        # Synthetic detection for live interactive demonstration
        w_box = [int(w * 0.25), int(h * 0.2), int(w * 0.55), int(h * 0.85)]
        hh_box = [int(w * 0.32), int(h * 0.18), int(w * 0.48), int(h * 0.35)]

        worker_det = {"class_name": "Person", "confidence": 0.94, "bbox": w_box}
        violation_det = {"class_name": "NO-Hardhat", "confidence": 0.89, "bbox": hh_box}

        if alert_classes is None or "Person" in alert_classes:
            detections.append(worker_det)
        if alert_classes is None or "NO-Hardhat" in alert_classes:
            detections.append(violation_det)

        annotated = np.array(frame, copy=True) if hasattr(frame, "copy") else frame
        return annotated, detections

