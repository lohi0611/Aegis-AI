"""
AEGIS-AI — PPE Compliance Evaluation Pipeline (Frame-Level & Worker-Level)
Explicitly distinguishes Object Detection accuracy, Frame-Level Violation Decision Accuracy,
and Worker-Level PPE Compliance Decision Accuracy.

Calculates Confusion Matrices, Accuracy, Precision, Recall (Safety Sensitivity),
Specificity, F1-Score, False Positive Rate (FPR), and Missed Hazard Rate (FNR).
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO

# Add parent directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.association.spatial import SpatialPPEAssociator, compute_iou
from src.compliance.rules import PPERuleEngine
from evaluation.utils import (
    load_eval_config,
    ensure_dir,
    get_hardware_info,
    save_json_report,
    save_csv_report,
)


def parse_yolo_labels_with_boxes(label_path: Path, img_w: int, img_h: int, class_mapping: Dict[int, str]) -> List[Dict[str, Any]]:
    """Parse YOLO label file and return bounding boxes in absolute coordinates."""
    if not label_path.exists():
        return []
    items = []
    with open(label_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                cls_id = int(parts[0])
                cx, cy, bw, bh = map(float, parts[1:5])
                x1 = (cx - bw / 2.0) * img_w
                y1 = (cy - bh / 2.0) * img_h
                x2 = (cx + bw / 2.0) * img_w
                y2 = (cy + bh / 2.0) * img_h
                items.append({
                    "class_id": cls_id,
                    "class_name": class_mapping.get(cls_id, f"Class_{cls_id}"),
                    "bbox": [x1, y1, x2, y2],
                    "confidence": 1.0,
                })
    return items


def compute_binary_metrics(tp: int, fp: int, tn: int, fn: int) -> Dict[str, float]:
    """Calculate full diagnostic metrics from a 2x2 confusion matrix."""
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0

    # Strict consistency verification
    assert 0.0 <= accuracy <= 1.0, f"Invalid accuracy: {accuracy}"
    assert 0.0 <= precision <= 1.0, f"Invalid precision: {precision}"
    assert 0.0 <= recall <= 1.0, f"Invalid recall: {recall}"
    assert 0.0 <= specificity <= 1.0, f"Invalid specificity: {specificity}"
    assert 0.0 <= f1 <= 1.0, f"Invalid F1: {f1}"
    assert 0.0 <= fpr <= 1.0, f"Invalid FPR: {fpr}"
    assert 0.0 <= fnr <= 1.0, f"Invalid FNR: {fnr}"

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall_sensitivity": round(recall, 4),
        "specificity": round(specificity, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate_fpr": round(fpr, 4),
        "false_negative_rate_miss_rate": round(fnr, 4),
    }


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
    Evaluate compliance decision logic across two distinct evaluation targets:
      1. Frame-Level PPE Violation Decision (Image-level safety alarm state)
      2. Worker-Level PPE Compliance Decision (Individual person-to-PPE association and state)
    """
    out_path = Path(output_dir)
    ensure_dir(out_path)

    print(f"\n=================================================================")
    print(f" AEGIS-AI: PPE Compliance Decision Evaluation (Frame & Worker Level)")
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
    associator = SpatialPPEAssociator(containment_threshold=0.35)
    rule_engine = PPERuleEngine(require_hardhat=True, require_vest=True, require_mask=False)

    violation_names = {"NO-Hardhat", "NO-Mask", "NO-Safety Vest"}

    img_files = sorted(list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")))
    print(f"Evaluating on {len(img_files)} ground-truth annotated frames...")

    # 1. Frame-Level Counters
    frame_tp = 0
    frame_fp = 0
    frame_tn = 0
    frame_fn = 0

    per_type_metrics = {vname: {"TP": 0, "FP": 0, "TN": 0, "FN": 0} for vname in violation_names}
    detailed_frame_records = []

    # 2. Worker-Level Counters
    worker_tp = 0
    worker_fp = 0
    worker_tn = 0
    worker_fn = 0
    total_gt_workers_count = 0
    total_pred_workers_count = 0
    detailed_worker_records = []

    for img_path in img_files:
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        h, w, _ = img.shape

        gt_items = parse_yolo_labels_with_boxes(lbl_path, w, h, class_mapping)

        # -------------------------------------------------------------
        # A. FRAME-LEVEL EVALUATION
        # -------------------------------------------------------------
        gt_violations = [item["class_name"] for item in gt_items if item["class_name"] in violation_names]
        is_gt_frame_violation = len(gt_violations) > 0

        # Predict
        results = model.predict(str(img_path), conf=conf_thresh, iou=iou_thresh, device=device, verbose=False)
        pred_boxes = results[0].boxes

        pred_items = []
        for b in pred_boxes:
            c_id = int(b.cls[0])
            c_name = class_mapping.get(c_id, f"Class_{c_id}")
            pred_items.append({
                "class_id": c_id,
                "class_name": c_name,
                "bbox": b.xyxy[0].tolist(),
                "confidence": float(b.conf[0]),
            })

        pred_violations = [item["class_name"] for item in pred_items if item["class_name"] in violation_names]
        is_pred_frame_violation = len(pred_violations) > 0

        decision_category = ""
        if is_gt_frame_violation and is_pred_frame_violation:
            frame_tp += 1
            decision_category = "True Positive (Correct Frame Violation)"
        elif not is_gt_frame_violation and is_pred_frame_violation:
            frame_fp += 1
            decision_category = "False Positive (Frame False Alarm)"
        elif not is_gt_frame_violation and not is_pred_frame_violation:
            frame_tn += 1
            decision_category = "True Negative (Correct Compliant Frame)"
        elif is_gt_frame_violation and not is_pred_frame_violation:
            frame_fn += 1
            decision_category = "False Negative (Missed Frame Hazard)"

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

        detailed_frame_records.append({
            "image": img_path.name,
            "gt_has_violation": is_gt_frame_violation,
            "pred_has_violation": is_pred_frame_violation,
            "gt_violations": "|".join(gt_violations) if gt_violations else "Compliant",
            "pred_violations": "|".join(pred_violations) if pred_violations else "Compliant",
            "frame_decision_category": decision_category,
        })

        # -------------------------------------------------------------
        # B. WORKER-LEVEL EVALUATION (Spatial Association + Rule Engine)
        # -------------------------------------------------------------
        gt_persons = [item for item in gt_items if item["class_name"] == "Person"]
        gt_ppe = [item for item in gt_items if item["class_name"] != "Person"]
        for idx, p in enumerate(gt_persons):
            p["track_id"] = f"GT_{idx}"

        gt_associated, _ = associator.associate(gt_persons, gt_ppe)
        gt_worker_states = [rule_engine.evaluate_worker(w_rec) for w_rec in gt_associated]

        pred_persons = []
        pred_ppe = []
        p_counter = 0
        for item in pred_items:
            if item["class_name"] == "Person":
                pred_persons.append({
                    "bbox": item["bbox"],
                    "track_id": f"PRED_{p_counter}",
                    "confidence": item["confidence"],
                })
                p_counter += 1
            else:
                pred_ppe.append({
                    "class_name": item["class_name"],
                    "bbox": item["bbox"],
                    "confidence": item["confidence"],
                })

        pred_associated, _ = associator.associate(pred_persons, pred_ppe)
        pred_worker_states = [rule_engine.evaluate_worker(w_rec) for w_rec in pred_associated]

        total_gt_workers_count += len(gt_worker_states)
        total_pred_workers_count += len(pred_worker_states)

        matched_pred_indices = set()
        for g_idx, gt_w in enumerate(gt_worker_states):
            best_iou = 0.0
            best_p_idx = -1
            for p_idx, pr_w in enumerate(pred_worker_states):
                if p_idx in matched_pred_indices:
                    continue
                iou = compute_iou(gt_w["bbox"], pr_w["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_p_idx = p_idx

            gt_is_viol = not gt_w["is_compliant"]

            if best_p_idx >= 0 and best_iou >= 0.50:
                matched_pred_indices.add(best_p_idx)
                pr_w = pred_worker_states[best_p_idx]
                pr_is_viol = not pr_w["is_compliant"]

                if gt_is_viol and pr_is_viol:
                    worker_tp += 1
                    w_cat = "True Positive"
                elif not gt_is_viol and pr_is_viol:
                    worker_fp += 1
                    w_cat = "False Positive"
                elif not gt_is_viol and not pr_is_viol:
                    worker_tn += 1
                    w_cat = "True Negative"
                elif gt_is_viol and not pr_is_viol:
                    worker_fn += 1
                    w_cat = "False Negative"

                detailed_worker_records.append({
                    "image": img_path.name,
                    "gt_worker_id": gt_w["worker_id"],
                    "gt_status": gt_w["status"],
                    "pred_worker_id": pr_w["worker_id"],
                    "pred_status": pr_w["status"],
                    "iou": round(best_iou, 3),
                    "decision_category": w_cat,
                })
            else:
                # Missed GT Person Detection
                if gt_is_viol:
                    worker_fn += 1
                    w_cat = "False Negative (Missed Person Detection)"
                else:
                    worker_tn += 1
                    w_cat = "True Negative (Missed Person Detection)"

                detailed_worker_records.append({
                    "image": img_path.name,
                    "gt_worker_id": gt_w["worker_id"],
                    "gt_status": gt_w["status"],
                    "pred_worker_id": "Unmatched",
                    "pred_status": "Not Detected",
                    "iou": 0.0,
                    "decision_category": w_cat,
                })

        # Spurious predicted workers (False Alarms)
        for p_idx, pr_w in enumerate(pred_worker_states):
            if p_idx not in matched_pred_indices:
                if not pr_w["is_compliant"]:
                    worker_fp += 1
                    w_cat = "False Positive (Spurious Worker Detection)"
                else:
                    worker_tn += 1
                    w_cat = "True Negative (Spurious Worker Detection)"

                detailed_worker_records.append({
                    "image": img_path.name,
                    "gt_worker_id": "Unmatched",
                    "gt_status": "No Ground Truth Worker",
                    "pred_worker_id": pr_w["worker_id"],
                    "pred_status": pr_w["status"],
                    "iou": 0.0,
                    "decision_category": w_cat,
                })

    # Compute Frame-Level Metrics
    frame_metrics = compute_binary_metrics(frame_tp, frame_fp, frame_tn, frame_fn)

    # Compute Worker-Level Metrics
    worker_metrics = compute_binary_metrics(worker_tp, worker_fp, worker_tn, worker_fn)

    # Per violation category breakdown (Frame-Level)
    per_type_rows = []
    for vname, m in per_type_metrics.items():
        t_metrics = compute_binary_metrics(m["TP"], m["FP"], m["TN"], m["FN"])
        per_type_rows.append({
            "violation_type": vname,
            "TP": m["TP"],
            "FP": m["FP"],
            "TN": m["TN"],
            "FN": m["FN"],
            "accuracy": t_metrics["accuracy"],
            "precision": t_metrics["precision"],
            "recall": t_metrics["recall_sensitivity"],
            "f1_score": t_metrics["f1_score"],
            "miss_rate_fnr": t_metrics["false_negative_rate_miss_rate"],
        })
    per_type_df = pd.DataFrame(per_type_rows)

    # Master compliance report with distinct Frame-Level and Worker-Level scopes
    compliance_report = {
        "experiment": "PPE Compliance Decision Engine Evaluation (Frame & Worker Level)",
        "timestamp": get_hardware_info()["timestamp"],
        "dataset_split": str(data_split_dir),
        "frame_level_evaluation": {
            "total_evaluated_frames": len(img_files),
            "confusion_matrix": {
                "TP_correct_violations": frame_tp,
                "FP_false_alarms": frame_fp,
                "TN_correct_compliant": frame_tn,
                "FN_missed_hazards": frame_fn,
            },
            "metrics": {
                "frame_violation_decision_accuracy": frame_metrics["accuracy"],
                "frame_violation_precision": frame_metrics["precision"],
                "frame_violation_recall_sensitivity": frame_metrics["recall_sensitivity"],
                "frame_violation_specificity": frame_metrics["specificity"],
                "frame_violation_f1_score": frame_metrics["f1_score"],
                "frame_false_positive_rate_fpr": frame_metrics["false_positive_rate_fpr"],
                "frame_false_negative_rate_fnr": frame_metrics["false_negative_rate_miss_rate"],
            },
        },
        "worker_level_evaluation": {
            "total_ground_truth_workers": total_gt_workers_count,
            "total_predicted_workers": total_pred_workers_count,
            "confusion_matrix": {
                "TP_correct_worker_violations": worker_tp,
                "FP_false_alarms_on_workers": worker_fp,
                "TN_correct_compliant_workers": worker_tn,
                "FN_missed_worker_hazards": worker_fn,
            },
            "metrics": {
                "worker_compliance_decision_accuracy": worker_metrics["accuracy"],
                "worker_violation_precision": worker_metrics["precision"],
                "worker_violation_recall_sensitivity": worker_metrics["recall_sensitivity"],
                "worker_violation_specificity": worker_metrics["specificity"],
                "worker_violation_f1_score": worker_metrics["f1_score"],
                "worker_false_positive_rate_fpr": worker_metrics["false_positive_rate_fpr"],
                "worker_false_negative_rate_fnr": worker_metrics["false_negative_rate_miss_rate"],
            },
        },
        "per_violation_category_metrics": per_type_rows,
    }

    # Save outputs
    save_json_report(compliance_report, out_path / "compliance_metrics.json")
    save_csv_report(per_type_df, out_path / "per_violation_compliance.csv")
    save_csv_report(pd.DataFrame(detailed_frame_records), out_path / "compliance_frame_decisions.csv")
    save_csv_report(pd.DataFrame(detailed_worker_records), out_path / "compliance_worker_decisions.csv")

    # Print clean formatted console summary
    print("\n" + "=" * 70)
    print(" PPE COMPLIANCE DECISION EVALUATION SUMMARY")
    print("=" * 70)
    print(" [1] FRAME-LEVEL PPE VIOLATION DECISION METRICS (N=82 frames):")
    print(f"     Accuracy:    {frame_metrics['accuracy']:.4f} ({frame_metrics['accuracy']*100:.2f}%)")
    print(f"     Precision:   {frame_metrics['precision']:.4f} ({frame_metrics['precision']*100:.2f}%)")
    print(f"     Recall:      {frame_metrics['recall_sensitivity']:.4f} ({frame_metrics['recall_sensitivity']*100:.2f}%)")
    print(f"     F1-Score:    {frame_metrics['f1_score']:.4f} ({frame_metrics['f1_score']*100:.2f}%)")
    print(f"     FPR:         {frame_metrics['false_positive_rate_fpr']:.4f} ({frame_metrics['false_positive_rate_fpr']*100:.2f}%)")
    print(f"     FNR:         {frame_metrics['false_negative_rate_miss_rate']:.4f} ({frame_metrics['false_negative_rate_miss_rate']*100:.2f}%)")
    print(f"     CM: TP={frame_tp}, FP={frame_fp}, TN={frame_tn}, FN={frame_fn}")
    print("-" * 70)
    print(f" [2] WORKER-LEVEL PPE COMPLIANCE METRICS (N={total_gt_workers_count} GT Workers):")
    print(f"     Accuracy:    {worker_metrics['accuracy']:.4f} ({worker_metrics['accuracy']*100:.2f}%)")
    print(f"     Precision:   {worker_metrics['precision']:.4f} ({worker_metrics['precision']*100:.2f}%)")
    print(f"     Recall:      {worker_metrics['recall_sensitivity']:.4f} ({worker_metrics['recall_sensitivity']*100:.2f}%)")
    print(f"     F1-Score:    {worker_metrics['f1_score']:.4f} ({worker_metrics['f1_score']*100:.2f}%)")
    print(f"     FPR:         {worker_metrics['false_positive_rate_fpr']:.4f} ({worker_metrics['false_positive_rate_fpr']*100:.2f}%)")
    print(f"     FNR:         {worker_metrics['false_negative_rate_miss_rate']:.4f} ({worker_metrics['false_negative_rate_miss_rate']*100:.2f}%)")
    print(f"     CM: TP={worker_tp}, FP={worker_fp}, TN={worker_fp+worker_tn-worker_fp}, FN={worker_fn}")
    print("=" * 70 + "\n")

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
