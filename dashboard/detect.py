import os
import cv2
from ultralytics import YOLO

class PPEDetector:
    def __init__(self, model_path=None, conf=0.5):
        if model_path is None:
            # Resolve model path relative to this script's directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            
            potential_paths = [
                os.path.join(project_root, "models", "yolov8_ppe.pt"),
                os.path.join(current_dir, "models", "yolov8_ppe.pt"),
                "models/yolov8_ppe.pt"
            ]
            
            for p in potential_paths:
                if os.path.exists(p):
                    model_path = p
                    break
            
            if model_path is None:
                model_path = "models/yolov8_ppe.pt" # Fallback
        
        self.model = YOLO(model_path)
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

    def detect(self, frame):
        results = self.model.predict(frame, conf=self.conf, verbose=False)
        annotated = results[0].plot()

        detections = []
        boxes = results[0].boxes

        for box in boxes:
            cls_idx = int(box.cls[0])
            class_name = self.model.names[cls_idx]

            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({
                "class_name": class_name,
                "confidence": round(conf, 2),
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                }
            })

        return annotated, detections
