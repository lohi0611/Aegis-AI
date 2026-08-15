"""
AEGIS-AI — Empirical Ablation Study
Scientifically measures the marginal contribution of each system component:
  1. Base YOLOv8 Detector Only (Raw frame-level detections)
  2. Detector + Spatial Person-PPE Association Rules
  3. Full AEGIS Pipeline (Detector + Association + Temporal Hysteresis Confirmation)
Calculates True Positives, False Alarms (FP), Missed Hazards (FN), Precision, Recall, and F1.
"""
import os
import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from ultralytics import YOLO

# Add parent directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.compliance.engine import ComplianceEngine
from src.compliance.rules import PPERuleEngine
from evaluation.utils import (
    load_eval_config,
    ensure_dir,
    get_hardware_info,
    save_json_report,
    save_csv_report,
)


def parse_ground_truth(label_path: Path, class_mapping: dict) -> list:
    """Extract ground truth class names from label file."""
    if not label_path.exists():
        return []
    classes = []
    with open(label_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                cid = int(parts[0])
                if cid in class_mapping:
                    classes.append(class_mapping[cid])
    return classes


def run_ablation_study(
    model_path: str,
    data_split_dir: str,
    class_mapping: dict,
    conf_thresh: float = 0.25,
    device: str = "cpu",
    output_dir: str = "evaluation/results/ablation_study",
) -> dict:
    """
    Execute controlled ablation experiment comparing component configurations.
    """
    out_path = Path(output_dir)
    ensure_dir(out_path)

    print(f"\n=================================================================")
    print(f" AEGIS-AI: Component Ablation Study")
    print(f" Model:     {model_path}")
    print(f" Split Dir: {data_split_dir}")
    print(f"=================================================================\n")

    split_path = Path(data_split_dir)
    img_dir = split_path / "images"
    lbl_dir = split_path / "labels"

    model = YOLO(model_path)
    img_files = sorted(list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")))

    violation_types = {"NO-Hardhat", "NO-Safety Vest", "NO-Mask"}

    # Track metrics for 3 configurations
    configs = {
        "Config A: Base YOLOv8 Detector Only": {"TP": 0, "FP": 0, "TN": 0, "FN": 0},
        "Config B: Detector + Spatial Association Rules": {"TP": 0, "FP": 0, "TN": 0, "FN": 0},
        "Config C: Full AEGIS (Detector + Association + Temporal Filter)": {"TP": 0, "FP": 0, "TN": 0, "FN": 0},
    }

    full_engine = ComplianceEngine(
        require_hardhat=True,
        require_vest=True,
        require_mask=False,
        violation_confirm_frames=2,
        resolution_confirm_frames=3,
    )
    rule_engine_standalone = PPERuleEngine(require_hardhat=True, require_vest=True, require_mask=False)

    for img_path in img_files:
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        gt_classes = parse_ground_truth(lbl_path, class_mapping)
        gt_has_violation = any(c in violation_types for c in gt_classes)

        # Predict with YOLOv8
        results = model.predict(str(img_path), conf=conf_thresh, device=device, verbose=False)
        boxes = results[0].boxes
        
        raw_detections = []
        person_dets = []
        ppe_dets = []

        for b in boxes:
            cls_id = int(b.cls[0])
            cname = class_mapping.get(cls_id, f"Class_{cls_id}")
            bbox = [int(x) for x in b.xyxy[0].tolist()]
            conf = float(b.conf[0])
            det_item = {"class_name": cname, "bbox": bbox, "confidence": conf}
            raw_detections.append(det_item)
            if cname == "Person":
                person_dets.append(det_item)
            else:
                ppe_dets.append(det_item)

        # -------------------------------------------------------------
        # Config A: Base Detector (Flag violation if any negative class detected)
        # -------------------------------------------------------------
        raw_has_violation = any(d["class_name"] in violation_types for d in raw_detections)
        if gt_has_violation and raw_has_violation:
            configs["Config A: Base YOLOv8 Detector Only"]["TP"] += 1
        elif not gt_has_violation and raw_has_violation:
            configs["Config A: Base YOLOv8 Detector Only"]["FP"] += 1
        elif not gt_has_violation and not raw_has_violation:
            configs["Config A: Base YOLOv8 Detector Only"]["TN"] += 1
        elif gt_has_violation and not raw_has_violation:
            configs["Config A: Base YOLOv8 Detector Only"]["FN"] += 1

        # -------------------------------------------------------------
        # Config B: Detector + Spatial Association (Worker-Level Rules, No Temporal)
        # -------------------------------------------------------------
        workers, unassigned = full_engine.associator.associate(person_dets, ppe_dets)
        eval_workers = [rule_engine_standalone.evaluate_worker(w) for w in workers]
        assoc_has_violation = any(w["status"] == "Violation" for w in eval_workers) or any(p["class_name"] in violation_types for p in unassigned)
        
        if gt_has_violation and assoc_has_violation:
            configs["Config B: Detector + Spatial Association Rules"]["TP"] += 1
        elif not gt_has_violation and assoc_has_violation:
            configs["Config B: Detector + Spatial Association Rules"]["FP"] += 1
        elif not gt_has_violation and not assoc_has_violation:
            configs["Config B: Detector + Spatial Association Rules"]["TN"] += 1
        elif gt_has_violation and not assoc_has_violation:
            configs["Config B: Detector + Spatial Association Rules"]["FN"] += 1

        # -------------------------------------------------------------
        # Config C: Full AEGIS (Detector + Association + Temporal Hysteresis Filter)
        # -------------------------------------------------------------
        engine_out = full_engine.process_frame_detections(raw_detections)
        full_has_violation = engine_out["site_has_violation"]

        if gt_has_violation and full_has_violation:
            configs["Config C: Full AEGIS (Detector + Association + Temporal Filter)"]["TP"] += 1
        elif not gt_has_violation and full_has_violation:
            configs["Config C: Full AEGIS (Detector + Association + Temporal Filter)"]["FP"] += 1
        elif not gt_has_violation and not full_has_violation:
            configs["Config C: Full AEGIS (Detector + Association + Temporal Filter)"]["TN"] += 1
        elif gt_has_violation and not full_has_violation:
            configs["Config C: Full AEGIS (Detector + Association + Temporal Filter)"]["FN"] += 1

    # Format ablation table
    ablation_rows = []
    for cfg_name, stats in configs.items():
        tp = stats["TP"]
        fp = stats["FP"]
        tn = stats["TN"]
        fn = stats["FN"]
        tot = tp + fp + tn + fn
        acc = (tp + tn) / tot if tot > 0 else 0.0
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0

        ablation_rows.append({
            "Configuration Architecture": cfg_name,
            "True Positives (TP)": tp,
            "False Alarms (FP)": fp,
            "Missed Hazards (FN)": fn,
            "Accuracy (%)": round(acc * 100, 2),
            "Precision (%)": round(p * 100, 2),
            "Recall (Sens. %)": round(r * 100, 2),
            "F1-Score (%)": round(f1 * 100, 2),
            "False Alarm Rate (FPR %)": round(fpr * 100, 2),
        })

    ablation_df = pd.DataFrame(ablation_rows)

    report = {
        "experiment": "AEGIS Architecture Ablation Study",
        "timestamp": get_hardware_info()["timestamp"],
        "dataset_split": str(data_split_dir),
        "total_frames_evaluated": len(img_files),
        "ablation_results": ablation_rows,
    }

    # Save outputs
    save_json_report(report, out_path / "ablation_metrics.json")
    save_csv_report(ablation_df, out_path / "ablation_metrics.csv")

    # Print summary
    print("\n" + "=" * 85)
    print(" ABLATION STUDY: COMPONENT CONTRIBUTIONS")
    print("=" * 85)
    print(ablation_df.to_string(index=False))
    print("=" * 85 + "\n")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS-AI Ablation Study")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or 0)")
    args = parser.parse_args()

    cfg = load_eval_config(args.config)
    split_dir = REPO_ROOT / cfg["dataset"]["splits"]["test"]

    run_ablation_study(
        model_path=cfg["model"]["path"],
        data_split_dir=str(split_dir),
        class_mapping=cfg["dataset"]["classes"],
        conf_thresh=cfg["model"]["conf_threshold"],
        device=args.device or cfg["device"],
        output_dir="evaluation/results/ablation_study",
    )
