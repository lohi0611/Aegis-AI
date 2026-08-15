"""
AEGIS-AI — PPE Compliance Rule Engine Evaluation
Evaluates the end-to-end PPE Compliance Monitoring System.
Explicitly distinguishes Object Detection accuracy from Compliance Decision Accuracy.
Calculates Compliance Accuracy, Violation Precision, Violation Recall (Safety Sensitivity),
False Alarm Rate (FPR), Missed Hazard Rate (FNR), and Decision Confusion Matrices.
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
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


def parse_yolo_label_file(label_path: Path) -> List[int]:
    """Parse YOLO label file and return list of class IDs present."""
    if not label_path.exists():
        return []
    class_ids = []
    with open(label_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                class_ids.append(int(parts[0]))
    return class_ids


def evaluate_compliance(
    model_path: str,
    data_split_dir: str,
    class_mapping: Dict[int, str],
    conf_thresh: float = 0.25,
    iou_thresh: float = 0.45,
    device: str = "cpu",
    output_dir: str = "evaluation/results/compliance",
) -> dict:
    """
    Evaluate compliance decision logic against ground truth image annotations.
    """
    out_path = Path(output_dir)
    ensure_dir(out_path)

    print(f"\n=================================================================")
    print(f" AEGIS-AI: PPE Compliance Decision Engine Evaluation")
    print(f" Model:       {model_path}")
    print(f" Split Dir:   {data_split_dir}")
    print(f" Conf Thresh: {conf_thresh} | IoU: {iou_thresh} | Device: {device}")
    print(f"=================================================================\n")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model weights not found at: {model_path}")

    split_path = Path(data_split_dir)
    img_dir = split_path / "images"
    lbl_dir = split_path / "labels"

    if not img_dir.exists() or not lbl_dir.exists():
        raise FileNotFoundError(f"Missing images/labels directory in {data_split_dir}")

    model = YOLO(model_path)

    # Identify violation classes by index
    # 2: NO-Hardhat, 3: NO-Mask, 4: NO-Safety Vest
    violation_names = {"NO-Hardhat", "NO-Mask", "NO-Safety Vest"}
    violation_indices = {k for k, v in class_mapping.items() if v in violation_names}

    img_files = sorted(list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")))
    print(f"Evaluating on {len(img_files)} ground-truth annotated frames...")

    tp = 0  # GT Violation & Pred Violation
    fp = 0  # GT Compliant & Pred Violation (False Alarm)
    tn = 0  # GT Compliant & Pred Compliant
    fn = 0  # GT Violation & Pred Compliant (Missed Hazard - Critical!)

    # Per-violation-type counters
    per_type_metrics = {vname: {"TP": 0, "FP": 0, "TN": 0, "FN": 0} for vname in violation_names}

    detailed_records = []

    for img_path in img_files:
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        gt_classes = parse_yolo_label_file(lbl_path)

        # Ground truth status
        gt_violations = [class_mapping[c] for c in gt_classes if c in class_mapping and class_mapping[c] in violation_names]
        is_gt_violation = len(gt_violations) > 0

        # Predict
        results = model.predict(str(img_path), conf=conf_thresh, iou=iou_thresh, device=device, verbose=False)
        pred_classes = [int(b.cls[0]) for b in results[0].boxes]
        pred_violations = [class_mapping[c] for c in pred_classes if c in class_mapping and class_mapping[c] in violation_names]
        is_pred_violation = len(pred_violations) > 0

        # Overall compliance decision classification
        decision_category = ""
        if is_gt_violation and is_pred_violation:
            tp += 1
            decision_category = "True Positive (Correct Violation Flag)"
        elif not is_gt_violation and is_pred_violation:
            fp += 1
            decision_category = "False Positive (False Alarm)"
        elif not is_gt_violation and not is_pred_violation:
            tn += 1
            decision_category = "True Negative (Correct Compliant Flag)"
        elif is_gt_violation and not is_pred_violation:
            fn += 1
            decision_category = "False Negative (Missed Hazard)"

        # Per violation category evaluation
        for vname in violation_names:
            gt_has_v = vname in gt_violations
            pred_has_v = vname in pred_violations
            if gt_has_v and pred_has_v:
                per_type_metrics[vname]["TP"] += 1
            elif not gt_has_v and pred_has_v:
                per_type_metrics[vname]["FP"] += 1
            elif not gt_has_v and not pred_has_v:
                per_type_metrics[vname]["TN"] += 1
            elif gt_has_v and not pred_has_v:
                per_type_metrics[vname]["FN"] += 1

        detailed_records.append({
            "image": img_path.name,
            "gt_has_violation": is_gt_violation,
            "pred_has_violation": is_pred_violation,
            "gt_violations": "|".join(gt_violations) if gt_violations else "Compliant",
            "pred_violations": "|".join(pred_violations) if pred_violations else "Compliant",
            "decision_category": decision_category,
        })

    total_frames = len(img_files)
    accuracy = (tp + tn) / total_frames if total_frames > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0

    # Per violation type stats
    per_type_rows = []
    for vname, m in per_type_metrics.items():
        t_tp, t_fp, t_tn, t_fn = m["TP"], m["FP"], m["TN"], m["FN"]
        t_total = t_tp + t_fp + t_tn + t_fn
        t_acc = (t_tp + t_tn) / t_total if t_total > 0 else 0.0
        t_p = t_tp / (t_tp + t_fp) if (t_tp + t_fp) > 0 else 0.0
        t_r = t_tp / (t_tp + t_fn) if (t_tp + t_fn) > 0 else 0.0
        t_f1 = 2 * (t_p * t_r) / (t_p + t_r) if (t_p + t_r) > 0 else 0.0
        per_type_rows.append({
            "violation_type": vname,
            "TP": t_tp,
            "FP": t_fp,
            "TN": t_tn,
            "FN": t_fn,
            "accuracy": round(t_acc, 4),
            "precision": round(t_p, 4),
            "recall": round(t_r, 4),
            "f1_score": round(t_f1, 4),
            "miss_rate_fnr": round(t_fn / (t_tp + t_fn) if (t_tp + t_fn) > 0 else 0.0, 4),
        })

    per_type_df = pd.DataFrame(per_type_rows)

    compliance_report = {
        "experiment": "PPE Compliance Decision Engine Evaluation",
        "timestamp": get_hardware_info()["timestamp"],
        "dataset_split": str(data_split_dir),
        "total_evaluated_frames": total_frames,
        "confusion_matrix": {
            "TP_correct_violations": tp,
            "FP_false_alarms": fp,
            "TN_correct_compliant": tn,
            "FN_missed_hazards": fn,
        },
        "compliance_decision_metrics": {
            "overall_compliance_accuracy": round(accuracy, 4),
            "violation_precision": round(precision, 4),
            "violation_recall_sensitivity": round(recall, 4),
            "violation_f1_score": round(f1, 4),
            "false_positive_rate_fpr": round(fpr, 4),
            "false_negative_rate_miss_rate": round(fnr, 4),
        },
        "per_violation_category_metrics": per_type_rows,
    }

    # Save outputs
    save_json_report(compliance_report, out_path / "compliance_metrics.json")
    save_csv_report(per_type_df, out_path / "per_violation_compliance.csv")
    save_csv_report(pd.DataFrame(detailed_records), out_path / "compliance_frame_decisions.csv")

    # Print clean formatted console summary
    print("\n" + "=" * 65)
    print(" PPE COMPLIANCE DECISION EVALUATION SUMMARY")
    print("=" * 65)
    print(f" Total Frames Evaluated:       {total_frames}")
    print(f" Overall Decision Accuracy:    {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f" Violation Precision:          {precision:.4f} ({precision*100:.2f}%)")
    print(f" Violation Recall (Sensitivity): {recall:.4f} ({recall*100:.2f}%)")
    print(f" Violation F1-Score:           {f1:.4f} ({f1*100:.2f}%)")
    print(f" False Alarm Rate (FPR):       {fpr:.4f} ({fpr*100:.2f}%)")
    print(f" Missed Hazard Rate (FNR):     {fnr:.4f} ({fnr*100:.2f}%)")
    print("-" * 65)
    print(" Confusion Matrix:")
    print(f"   True Positives (Correct Violations):  {tp}")
    print(f"   False Positives (False Alarms):       {fp}")
    print(f"   True Negatives (Correct Compliant):   {tn}")
    print(f"   False Negatives (Missed Hazards):     {fn}")
    print("-" * 65)
    print(per_type_df.to_string(index=False))
    print("=" * 65 + "\n")

    return compliance_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS-AI Compliance Decision Engine Evaluation")
    parser.add_argument("--config", type=str, default=None, help="Path to evaluation config YAML")
    parser.add_argument("--split", type=str, default="test", choices=["test", "valid"], help="Dataset split to evaluate")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or 0)")
    args = parser.parse_args()

    cfg = load_eval_config(args.config)
    split_dir = REPO_ROOT / cfg["dataset"]["splits"][args.split]
    
    evaluate_compliance(
        model_path=cfg["model"]["path"],
        data_split_dir=str(split_dir),
        class_mapping=cfg["dataset"]["classes"],
        conf_thresh=cfg["model"]["conf_threshold"],
        iou_thresh=cfg["model"]["iou_threshold"],
        device=args.device or cfg["device"],
        output_dir=cfg["output_dirs"]["compliance"],
    )
