"""
AEGIS-AI — Cross-Validation Evaluation & Fold Aggregation
Aggregates cross-validation fold experiments, computing mean and standard deviation
across folds (mAP@50, mAP@50-95, Precision, Recall, F1) for empirical research reports.
"""
import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
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


def evaluate_cross_validation_folds(
    fold_model_paths: List[str] = None,
    fold_data_yamls: List[str] = None,
    device: str = "cpu",
    output_dir: str = "evaluation/results/cross_validation",
) -> Dict[str, Any]:
    """
    Evaluate multiple fold models and compute statistical distributions (Mean ± Std).
    """
    out_path = Path(output_dir)
    ensure_dir(out_path)

    print(f"\n=================================================================")
    print(f" AEGIS-AI: Cross-Validation & Statistical Aggregation Suite")
    print(f" Device: {device}")
    print(f"=================================================================\n")

    # Discover any fold checkpoints or fold data YAMLs in workspace
    discovered_folds = []
    
    # Check possible locations
    possible_dirs = [
        REPO_ROOT / "infosys" / "dataset" / "css-data" / "cross_validation",
        REPO_ROOT / "cross_validation",
        REPO_ROOT / "models" / "folds",
    ]

    for pdir in possible_dirs:
        if pdir.exists():
            for fold_sub in sorted(pdir.glob("fold*")):
                pt_file = fold_sub / "weights" / "best.pt"
                yaml_file = fold_sub / "data.yaml"
                if pt_file.exists() and yaml_file.exists():
                    discovered_folds.append((str(pt_file), str(yaml_file), fold_sub.name))

    fold_records = []

    if fold_model_paths and fold_data_yamls:
        # Custom user-provided lists
        for i, (m_path, d_yaml) in enumerate(zip(fold_model_paths, fold_data_yamls)):
            if os.path.exists(m_path) and os.path.exists(d_yaml):
                discovered_folds.append((m_path, d_yaml, f"Fold_{i+1}"))

    if not discovered_folds:
        print("[AEGIS-CV] No separate pre-trained k-fold model checkpoints found on disk.")
        print("[AEGIS-CV] Evaluating primary trained model (models/yolov8_ppe.pt) across validation & test splits as baseline.")
        
        primary_model = str(REPO_ROOT / "models" / "yolov8_ppe.pt")
        dataset_yaml = str(REPO_ROOT / "infosys" / "dataset" / "css-data" / "data.yaml")

        if os.path.exists(primary_model) and os.path.exists(dataset_yaml):
            m = YOLO(primary_model)
            for split_name in ["val", "test"]:
                print(f"--> Evaluating baseline split: {split_name}...")
                v_res = m.val(data=dataset_yaml, split=split_name, device=device, verbose=False)
                m_dict = v_res.results_dict
                p = float(m_dict.get("metrics/precision(B)", 0.0))
                r = float(m_dict.get("metrics/recall(B)", 0.0))
                f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
                m50 = float(m_dict.get("metrics/mAP50(B)", 0.0))
                m50_95 = float(m_dict.get("metrics/mAP50-95(B)", 0.0))

                fold_records.append({
                    "experiment_id": f"Baseline_{split_name.capitalize()}",
                    "split": split_name,
                    "precision": round(p, 4),
                    "recall": round(r, 4),
                    "f1_score": round(f1, 4),
                    "mAP50": round(m50, 4),
                    "mAP50_95": round(m50_95, 4),
                    "inference_speed_ms": round(v_res.speed.get("inference", 0.0), 2),
                })
    else:
        # Run evaluation on each discovered fold
        for m_path, d_yaml, fold_id in discovered_folds:
            print(f"--> Evaluating {fold_id} (Model: {m_path})...")
            m = YOLO(m_path)
            v_res = m.val(data=d_yaml, split="val", device=device, verbose=False)
            m_dict = v_res.results_dict

            p = float(m_dict.get("metrics/precision(B)", 0.0))
            r = float(m_dict.get("metrics/recall(B)", 0.0))
            f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
            m50 = float(m_dict.get("metrics/mAP50(B)", 0.0))
            m50_95 = float(m_dict.get("metrics/mAP50-95(B)", 0.0))

            fold_records.append({
                "experiment_id": fold_id,
                "split": "val",
                "precision": round(p, 4),
                "recall": round(r, 4),
                "f1_score": round(f1, 4),
                "mAP50": round(m50, 4),
                "mAP50_95": round(m50_95, 4),
                "inference_speed_ms": round(v_res.speed.get("inference", 0.0), 2),
            })

    fold_df = pd.DataFrame(fold_records)

    # Compute Statistical Aggregation (Mean ± Std)
    p_vals = fold_df["precision"].values
    r_vals = fold_df["recall"].values
    f1_vals = fold_df["f1_score"].values
    m50_vals = fold_df["mAP50"].values
    m50_95_vals = fold_df["mAP50_95"].values

    stats_summary = {
        "precision": {
            "mean": round(float(np.mean(p_vals)), 4),
            "std": round(float(np.std(p_vals)), 4),
            "formatted": f"{np.mean(p_vals):.4f} ± {np.std(p_vals):.4f}",
        },
        "recall": {
            "mean": round(float(np.mean(r_vals)), 4),
            "std": round(float(np.std(r_vals)), 4),
            "formatted": f"{np.mean(r_vals):.4f} ± {np.std(r_vals):.4f}",
        },
        "f1_score": {
            "mean": round(float(np.mean(f1_vals)), 4),
            "std": round(float(np.std(f1_vals)), 4),
            "formatted": f"{np.mean(f1_vals):.4f} ± {np.std(f1_vals):.4f}",
        },
        "mAP50": {
            "mean": round(float(np.mean(m50_vals)), 4),
            "std": round(float(np.std(m50_vals)), 4),
            "formatted": f"{np.mean(m50_vals):.4f} ± {np.std(m50_vals):.4f}",
        },
        "mAP50_95": {
            "mean": round(float(np.mean(m50_95_vals)), 4),
            "std": round(float(np.std(m50_95_vals)), 4),
            "formatted": f"{np.mean(m50_95_vals):.4f} ± {np.std(m50_95_vals):.4f}",
        },
    }

    cv_report = {
        "experiment": "Cross-Validation & Split Statistical Evaluation",
        "timestamp": get_hardware_info()["timestamp"],
        "num_evaluations": len(fold_records),
        "statistical_aggregation": stats_summary,
        "individual_runs": fold_records,
    }

    # Save outputs
    save_json_report(cv_report, out_path / "cross_val_summary.json")
    save_csv_report(fold_df, out_path / "cross_val_metrics.csv")

    # Print clean formatted console summary
    print("\n" + "=" * 70)
    print(" CROSS-VALIDATION & STATISTICAL AGGREGATION SUMMARY")
    print("=" * 70)
    print(fold_df.to_string(index=False))
    print("-" * 70)
    print(" STATISTICAL DISTRIBUTIONS (Mean ± Std Dev):")
    print(f"   Precision:   {stats_summary['precision']['formatted']}")
    print(f"   Recall:      {stats_summary['recall']['formatted']}")
    print(f"   F1-Score:    {stats_summary['f1_score']['formatted']}")
    print(f"   mAP@50:      {stats_summary['mAP50']['formatted']}")
    print(f"   mAP@50-95:   {stats_summary['mAP50_95']['formatted']}")
    print("=" * 70 + "\n")

    return cv_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS-AI Cross-Validation Aggregation")
    parser.add_argument("--config", type=str, default=None, help="Path to evaluation config YAML")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or 0)")
    args = parser.parse_args()

    cfg = load_eval_config(args.config)
    evaluate_cross_validation_folds(
        device=args.device or cfg["device"],
        output_dir=cfg["output_dirs"]["cross_validation"],
    )
