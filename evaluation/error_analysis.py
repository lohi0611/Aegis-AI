"""
AEGIS-AI — Error Analysis and Failure Mode Diagnostics
Categorizes false positives, false negatives, scale/resolution sensitivity,
and confidence distributions across dataset splits.
"""
import os
import sys
import argparse
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO

# Add parent directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluation.utils import (
    load_eval_config,
    ensure_dir,
    get_hardware_info,
    save_json_report,
    save_csv_report,
)


def compute_iou(boxA, boxB):
    """Compute Intersection over Union (IoU) between two bounding boxes [x1, y1, x2, y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / float(boxAArea + boxBArea - interArea) if (boxAArea + boxBArea - interArea) > 0 else 0.0
    return iou


def run_error_analysis(
    model_path: str,
    data_split_dir: str,
    class_mapping: dict,
    conf_thresh: float = 0.25,
    iou_thresh: float = 0.45,
    device: str = "cpu",
    output_dir: str = "evaluation/results/error_analysis",
) -> dict:
    """
    Perform granular failure mode analysis on ground truth versus model detections.
    """
    out_path = Path(output_dir)
    ensure_dir(out_path)

    print(f"\n=================================================================")
    print(f" AEGIS-AI: Error Analysis & Diagnostic Suite")
    print(f" Model:     {model_path}")
    print(f" Split Dir: {data_split_dir}")
    print(f"=================================================================\n")

    split_path = Path(data_split_dir)
    img_dir = split_path / "images"
    lbl_dir = split_path / "labels"

    model = YOLO(model_path)
    img_files = sorted(list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")))

    total_gt_boxes = 0
    total_pred_boxes = 0
    matched_tp = 0
    false_positives = 0
    false_negatives = 0
    class_confusions = []

    # Scale brackets: Small (<32x32 = area < 1024), Medium (1024-9216), Large (>9216)
    scale_stats = {
        "Small (<32x32)": {"total_gt": 0, "detected": 0, "missed": 0},
        "Medium (32x96)": {"total_gt": 0, "detected": 0, "missed": 0},
        "Large (>96x96)": {"total_gt": 0, "detected": 0, "missed": 0},
    }

    confidence_brackets = {
        "0.25 - 0.40 (Low)": 0,
        "0.40 - 0.70 (Medium)": 0,
        "0.70 - 1.00 (High)": 0,
    }

    per_class_errors = {cname: {"GT": 0, "Detected": 0, "Missed": 0, "FalseAlarms": 0} for cname in class_mapping.values()}

    for img_path in img_files:
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        h, w, _ = img.shape

        # Parse GT boxes in absolute coordinates
        gt_items = []
        if lbl_path.exists():
            with open(lbl_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cls_id = int(parts[0])
                        cx, cy, bw, bh = map(float, parts[1:5])
                        x1 = (cx - bw / 2.0) * w
                        y1 = (cy - bh / 2.0) * h
                        x2 = (cx + bw / 2.0) * w
                        y2 = (cy + bh / 2.0) * h
                        area = (x2 - x1) * (y2 - y1)
                        gt_items.append({
                            "cls_id": cls_id,
                            "cls_name": class_mapping.get(cls_id, f"Class_{cls_id}"),
                            "box": [x1, y1, x2, y2],
                            "area": area,
                            "matched": False,
                        })

        total_gt_boxes += len(gt_items)

        # Run Prediction
        results = model.predict(str(img_path), conf=conf_thresh, iou=iou_thresh, device=device, verbose=False)
        boxes = results[0].boxes
        total_pred_boxes += len(boxes)

        pred_items = []
        for b in boxes:
            p_cls_id = int(b.cls[0])
            p_conf = float(b.conf[0])
            p_box = b.xyxy[0].tolist()
            pred_items.append({
                "cls_id": p_cls_id,
                "cls_name": class_mapping.get(p_cls_id, f"Class_{p_cls_id}"),
                "conf": p_conf,
                "box": p_box,
                "matched": False,
            })

            # Tally confidence
            if p_conf < 0.40:
                confidence_brackets["0.25 - 0.40 (Low)"] += 1
            elif p_conf < 0.70:
                confidence_brackets["0.40 - 0.70 (Medium)"] += 1
            else:
                confidence_brackets["0.70 - 1.00 (High)"] += 1

        # Match Predictions to GT
        for pred in pred_items:
            best_iou = 0.0
            best_gt = None
            for gt in gt_items:
                if not gt["matched"] and gt["cls_id"] == pred["cls_id"]:
                    iou = compute_iou(pred["box"], gt["box"])
                    if iou > best_iou:
                        best_iou = iou
                        best_gt = gt

            if best_gt is not None and best_iou >= 0.50:
                best_gt["matched"] = True
                pred["matched"] = True
                matched_tp += 1
                per_class_errors[pred["cls_name"]]["Detected"] += 1
            else:
                # Check for class confusion
                for gt in gt_items:
                    iou = compute_iou(pred["box"], gt["box"])
                    if iou >= 0.50 and gt["cls_id"] != pred["cls_id"]:
                        class_confusions.append({
                            "gt_class": gt["cls_name"],
                            "pred_class": pred["cls_name"],
                            "conf": round(pred["conf"], 3),
                            "image": img_path.name,
                        })
                false_positives += 1
                per_class_errors[pred["cls_name"]]["FalseAlarms"] += 1

        # Count scale and missed GT items
        for gt in gt_items:
            per_class_errors[gt["cls_name"]]["GT"] += 1
            area = gt["area"]
            if area < (32 * 32):
                scale_cat = "Small (<32x32)"
            elif area < (96 * 96):
                scale_cat = "Medium (32x96)"
            else:
                scale_cat = "Large (>96x96)"

            scale_stats[scale_cat]["total_gt"] += 1
            if gt["matched"]:
                scale_stats[scale_cat]["detected"] += 1
            else:
                scale_stats[scale_cat]["missed"] += 1
                false_negatives += 1
                per_class_errors[gt["cls_name"]]["Missed"] += 1

    # Format scale sensitivity table
    scale_rows = []
    for scale_name, s in scale_stats.items():
        tot = s["total_gt"]
        det = s["detected"]
        recall_pct = round((det / tot) * 100, 2) if tot > 0 else 0.0
        scale_rows.append({
            "Object Scale": scale_name,
            "Total Ground Truth": tot,
            "Successfully Detected": det,
            "Missed Objects (FN)": s["missed"],
            "Detection Recall (%)": recall_pct,
        })
    scale_df = pd.DataFrame(scale_rows)

    # Format per-class error table
    class_error_rows = []
    for cname, stats in per_class_errors.items():
        gt_tot = stats["GT"]
        missed = stats["Missed"]
        fa = stats["FalseAlarms"]
        rec = round(((gt_tot - missed) / gt_tot) * 100, 2) if gt_tot > 0 else 0.0
        class_error_rows.append({
            "Class Name": cname,
            "Total GT": gt_tot,
            "Detected": stats["Detected"],
            "Missed (FN)": missed,
            "False Alarms (FP)": fa,
            "Recall (%)": rec,
        })
    class_error_df = pd.DataFrame(class_error_rows)

    # Error breakdown summary
    error_summary = {
        "experiment": "PPE Detection Error Analysis and Diagnostics",
        "timestamp": get_hardware_info()["timestamp"],
        "dataset_split": str(data_split_dir),
        "total_images": len(img_files),
        "overall_error_counts": {
            "total_ground_truth_objects": total_gt_boxes,
            "total_predicted_boxes": total_pred_boxes,
            "matched_true_positives": matched_tp,
            "false_positives_false_alarms": false_positives,
            "false_negatives_missed_ppe": false_negatives,
            "cross_class_confusions": len(class_confusions),
        },
        "scale_sensitivity_analysis": scale_rows,
        "confidence_distribution": confidence_brackets,
        "per_class_error_breakdown": class_error_rows,
        "class_confusion_examples": class_confusions[:20],
    }

    # Save outputs
    save_json_report(error_summary, out_path / "error_breakdown.json")
    save_csv_report(scale_df, out_path / "scale_sensitivity.csv")
    save_csv_report(class_error_df, out_path / "per_class_errors.csv")
    save_csv_report(pd.DataFrame(class_confusions), out_path / "class_confusions.csv")

    # Print clean formatted console summary
    print("\n" + "=" * 70)
    print(" ERROR ANALYSIS & SCALE SENSITIVITY SUMMARY")
    print("=" * 70)
    print(f" Total GT Objects:        {total_gt_boxes}")
    print(f" True Positives:          {matched_tp}")
    print(f" False Positives (FP):    {false_positives}")
    print(f" False Negatives (FN):    {false_negatives}")
    print(f" Cross-Class Confusions:  {len(class_confusions)}")
    print("-" * 70)
    print(" DETECTION RECALL BY OBJECT SCALE:")
    print(scale_df.to_string(index=False))
    print("-" * 70)
    print(" PER-CLASS ERROR BREAKDOWN:")
    print(class_error_df.to_string(index=False))
    print("=" * 70 + "\n")

    return error_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS-AI Error Analysis and Diagnostics")
    parser.add_argument("--config", type=str, default=None, help="Path to evaluation config YAML")
    parser.add_argument("--split", type=str, default="test", choices=["test", "valid"], help="Dataset split to evaluate")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or 0)")
    args = parser.parse_args()

    cfg = load_eval_config(args.config)
    split_dir = REPO_ROOT / cfg["dataset"]["splits"][args.split]

    run_error_analysis(
        model_path=cfg["model"]["path"],
        data_split_dir=str(split_dir),
        class_mapping=cfg["dataset"]["classes"],
        conf_thresh=cfg["model"]["conf_threshold"],
        iou_thresh=cfg["model"]["iou_threshold"],
        device=args.device or cfg["device"],
        output_dir=cfg["output_dirs"]["error_analysis"],
    )
