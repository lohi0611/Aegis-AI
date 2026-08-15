"""
AEGIS-AI — Model Detection Evaluation Pipeline
Evaluates YOLOv8 PPE detection on test/validation splits and generates quantitative research metrics.
Calculates Precision, Recall, F1, mAP@50, mAP@50-95, per-class metrics, and confusion matrices.
"""
import os
import sys
import shutil
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

from evaluation.utils import (
    load_eval_config,
    ensure_dir,
    get_hardware_info,
    save_json_report,
    save_csv_report,
)


def evaluate_model(
    model_path: str,
    data_yaml: str,
    split: str = "test",
    batch_size: int = 16,
    imgsz: int = 640,
    device: str = "cpu",
    conf_thresh: float = 0.25,
    iou_thresh: float = 0.45,
    output_dir: str = "evaluation/results/detection",
) -> dict:
    """
    Run evaluation on the test or validation dataset using Ultralytics YOLOv8 engine.
    Extracts comprehensive research metrics and saves reports.
    """
    out_path = Path(output_dir)
    ensure_dir(out_path)

    print(f"\n=================================================================")
    print(f" AEGIS-AI: Object Detection Model Evaluation")
    print(f" Model:      {model_path}")
    print(f" Dataset:    {data_yaml} (Split: {split})")
    print(f" Device:     {device} | ImgSz: {imgsz} | Batch: {batch_size}")
    print(f"=================================================================\n")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at: {model_path}")
    if not os.path.exists(data_yaml):
        raise FileNotFoundError(f"Dataset YAML not found at: {data_yaml}")

    model = YOLO(model_path)

    # Execute YOLO validation
    val_results = model.val(
        data=data_yaml,
        split=split,
        batch=batch_size,
        imgsz=imgsz,
        conf=conf_thresh,
        iou=iou_thresh,
        device=device,
        save_json=True,
        plots=True,
        verbose=True,
    )

    # Extract overall metrics
    metrics_dict = val_results.results_dict
    
    # Map metrics
    mp = float(metrics_dict.get("metrics/precision(B)", 0.0))
    mr = float(metrics_dict.get("metrics/recall(B)", 0.0))
    map50 = float(metrics_dict.get("metrics/mAP50(B)", 0.0))
    map50_95 = float(metrics_dict.get("metrics/mAP50-95(B)", 0.0))
    f1_score = 2 * (mp * mr) / (mp + mr) if (mp + mr) > 0 else 0.0

    class_names = model.names
    num_classes = len(class_names)

    # Per-class metrics
    per_class_data = []
    
    # Safely extract per-class AP50, AP50_95, P, R
    class_map50 = val_results.box.all_ap[:, 0] if hasattr(val_results.box, "all_ap") and len(val_results.box.all_ap) > 0 else [0.0]*num_classes
    class_map50_95 = val_results.box.maps if hasattr(val_results.box, "maps") and len(val_results.box.maps) > 0 else [0.0]*num_classes
    class_p = val_results.box.p if hasattr(val_results.box, "p") and len(val_results.box.p) > 0 else [0.0]*num_classes
    class_r = val_results.box.r if hasattr(val_results.box, "r") and len(val_results.box.r) > 0 else [0.0]*num_classes
    class_f1 = val_results.box.f1 if hasattr(val_results.box, "f1") and len(val_results.box.f1) > 0 else [0.0]*num_classes

    for i in range(num_classes):
        c_name = class_names.get(i, f"Class_{i}")
        p_val = float(class_p[i]) if i < len(class_p) else 0.0
        r_val = float(class_r[i]) if i < len(class_r) else 0.0
        f1_val = float(class_f1[i]) if i < len(class_f1) else (2 * p_val * r_val / (p_val + r_val) if (p_val + r_val) > 0 else 0.0)
        m50_val = float(class_map50[i]) if i < len(class_map50) else 0.0
        m50_95_val = float(class_map50_95[i]) if i < len(class_map50_95) else 0.0

        per_class_data.append({
            "class_id": i,
            "class_name": c_name,
            "precision": round(p_val, 4),
            "recall": round(r_val, 4),
            "f1_score": round(f1_val, 4),
            "mAP50": round(m50_val, 4),
            "mAP50_95": round(m50_95_val, 4),
        })

    per_class_df = pd.DataFrame(per_class_data)

    # Copy plots from YOLO run directory to evaluation/results/detection
    yolo_save_dir = Path(val_results.save_dir)
    plot_files = ["confusion_matrix.png", "confusion_matrix_normalized.png", 
                  "F1_curve.png", "PR_curve.png", "P_curve.png", "R_curve.png", "val_batch0_pred.jpg"]
    
    copied_plots = []
    for pf in plot_files:
        src = yolo_save_dir / pf
        if src.exists():
            dst = out_path / pf
            shutil.copy(src, dst)
            copied_plots.append(str(dst))

    # Comprehensive summary report
    summary_report = {
        "experiment": "YOLOv8 PPE Detection Evaluation",
        "timestamp": get_hardware_info()["timestamp"],
        "model_info": {
            "model_path": str(model_path),
            "classes": class_names,
            "num_classes": num_classes,
        },
        "evaluation_config": {
            "dataset_yaml": str(data_yaml),
            "split": split,
            "batch_size": batch_size,
            "imgsz": imgsz,
            "conf_threshold": conf_thresh,
            "iou_threshold": iou_thresh,
            "device": device,
        },
        "overall_metrics": {
            "precision": round(mp, 4),
            "recall": round(mr, 4),
            "f1_score": round(f1_score, 4),
            "mAP50": round(map50, 4),
            "mAP50_95": round(map50_95_val if 'map50_95_val' in locals() else map50_95, 4),
            "speed_inference_ms": round(val_results.speed.get("inference", 0.0), 2),
            "speed_preprocess_ms": round(val_results.speed.get("preprocess", 0.0), 2),
            "speed_loss_ms": round(val_results.speed.get("loss", 0.0), 2),
            "speed_postprocess_ms": round(val_results.speed.get("postprocess", 0.0), 2),
        },
        "hardware_telemetry": get_hardware_info(),
        "per_class_metrics": per_class_data,
        "generated_artifacts": copied_plots,
    }

    # Save outputs
    save_json_report(summary_report, out_path / "metrics.json")
    save_csv_report(per_class_df, out_path / "per_class_metrics.csv")

    # Print clean formatted console summary
    print("\n" + "=" * 65)
    print(" DETECTION PERFORMANCE EVALUATION SUMMARY")
    print("=" * 65)
    print(f" Precision:       {mp:.4f} ({mp*100:.2f}%)")
    print(f" Recall:          {mr:.4f} ({mr*100:.2f}%)")
    print(f" F1-Score:        {f1_score:.4f} ({f1_score*100:.2f}%)")
    print(f" mAP@50:          {map50:.4f} ({map50*100:.2f}%)")
    print(f" mAP@50-95:       {map50_95:.4f} ({map50_95*100:.2f}%)")
    print("-" * 65)
    print(per_class_df.to_string(index=False))
    print("=" * 65 + "\n")

    return summary_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS-AI YOLOv8 Detection Model Evaluation")
    parser.add_argument("--config", type=str, default=None, help="Path to evaluation config YAML")
    parser.add_argument("--split", type=str, default="test", choices=["test", "val"], help="Dataset split")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or 0)")
    args = parser.parse_args()

    cfg = load_eval_config(args.config)
    
    evaluate_model(
        model_path=cfg["model"]["path"],
        data_yaml=cfg["dataset"]["yaml_path"],
        split=args.split,
        batch_size=cfg["detection_eval"]["batch_size"],
        imgsz=cfg["model"]["input_resolution"][0],
        device=args.device or cfg["device"],
        conf_thresh=cfg["model"]["conf_threshold"],
        iou_thresh=cfg["model"]["iou_threshold"],
        output_dir=cfg["output_dirs"]["detection"],
    )
