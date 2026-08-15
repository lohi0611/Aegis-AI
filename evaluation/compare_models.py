"""
AEGIS-AI — Model Variant Architecture & Speed-Accuracy Trade-off Comparison
Compares model variants on size (MB), parameter count, mAP@50, mAP@50-95,
precision, recall, F1, and real-time FPS throughput.
"""
import os
import sys
import time
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


def compare_models(
    model_paths: dict = None,
    data_yaml: str = None,
    split: str = "test",
    device: str = "cpu",
    imgsz: int = 640,
    output_dir: str = "evaluation/results/model_comparison",
) -> dict:
    """
    Compare multiple YOLOv8 checkpoints on accuracy, parameter size, and latency.
    """
    out_path = Path(output_dir)
    ensure_dir(out_path)

    if model_paths is None:
        model_paths = {
            "YOLOv8n-PPE (Custom Trained)": str(REPO_ROOT / "models" / "yolov8_ppe.pt"),
            "YOLOv8n (Pretrained Baseline)": str(REPO_ROOT / "infosys" / "dataset" / "results_yolov8n_100e" / "kaggle" / "working" / "yolov8n.pt"),
        }

    if data_yaml is None:
        data_yaml = str(REPO_ROOT / "infosys" / "dataset" / "css-data" / "data.yaml")

    print(f"\n=================================================================")
    print(f" AEGIS-AI: Model Architecture & Speed-Accuracy Comparison")
    print(f" Dataset:    {data_yaml} (Split: {split})")
    print(f" Device:     {device} | ImgSz: {imgsz}")
    print(f" Models:     {list(model_paths.keys())}")
    print(f"=================================================================\n")

    comparison_records = []

    for name, m_path in model_paths.items():
        if not os.path.exists(m_path):
            print(f"[AEGIS-COMPARE] Skipping {name} (path not found: {m_path})")
            continue

        print(f"--> Evaluating {name} ({m_path})...")
        file_size_mb = round(os.path.getsize(m_path) / (1024 * 1024), 2)

        model = YOLO(m_path)
        
        # Get parameter count if model structure is loaded
        param_count = sum(p.numel() for p in model.model.parameters()) if hasattr(model, "model") and model.model else 0
        param_count_m = round(param_count / 1e6, 2)

        try:
            val_res = model.val(data=data_yaml, split=split, device=device, verbose=False)
            m_dict = val_res.results_dict

            p = float(m_dict.get("metrics/precision(B)", 0.0))
            r = float(m_dict.get("metrics/recall(B)", 0.0))
            f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
            m50 = float(m_dict.get("metrics/mAP50(B)", 0.0))
            m50_95 = float(m_dict.get("metrics/mAP50-95(B)", 0.0))

            inf_ms = float(val_res.speed.get("inference", 0.0))
            prep_ms = float(val_res.speed.get("preprocess", 0.0))
            post_ms = float(val_res.speed.get("postprocess", 0.0))
            e2e_ms = inf_ms + prep_ms + post_ms
            fps = round(1000.0 / e2e_ms, 2) if e2e_ms > 0 else 0.0
        except Exception as e:
            print(f"[AEGIS-COMPARE] Model evaluation note for {name}: {e}")
            # Benchmark speed on dummy/sample tensor if class heads differ
            t0 = time.perf_counter()
            for _ in range(20):
                _ = model.predict(np.zeros((imgsz, imgsz, 3), dtype=np.uint8), device=device, verbose=False)
            t_total = (time.perf_counter() - t0) / 20.0 * 1000.0
            p, r, f1, m50, m50_95 = 0.0, 0.0, 0.0, 0.0, 0.0
            inf_ms, e2e_ms = t_total, t_total
            fps = round(1000.0 / e2e_ms, 2) if e2e_ms > 0 else 0.0

        comparison_records.append({
            "model_name": name,
            "file_size_mb": file_size_mb,
            "params_millions": param_count_m,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1_score": round(f1, 4),
            "mAP50": round(m50, 4),
            "mAP50_95": round(m50_95, 4),
            "inference_latency_ms": round(inf_ms, 2),
            "e2e_latency_ms": round(e2e_ms, 2),
            "throughput_fps": fps,
        })

    comp_df = pd.DataFrame(comparison_records)

    report = {
        "experiment": "Model Architecture & Speed-Accuracy Comparison",
        "timestamp": get_hardware_info()["timestamp"],
        "dataset": data_yaml,
        "split": split,
        "device": device,
        "comparison_results": comparison_records,
    }

    # Save outputs
    save_json_report(report, out_path / "model_comparison.json")
    save_csv_report(comp_df, out_path / "model_comparison.csv")

    # Print clean formatted console summary
    print("\n" + "=" * 85)
    print(" MODEL VARIANT & SPEED-ACCURACY COMPARISON SUMMARY")
    print("=" * 85)
    print(comp_df.to_string(index=False))
    print("=" * 85 + "\n")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS-AI Model Architecture & Speed-Accuracy Comparison")
    parser.add_argument("--config", type=str, default=None, help="Path to evaluation config YAML")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or 0)")
    args = parser.parse_args()

    cfg = load_eval_config(args.config)
    
    compare_models(
        data_yaml=cfg["dataset"]["yaml_path"],
        split=cfg["detection_eval"]["split"],
        device=args.device or cfg["device"],
        imgsz=cfg["model"]["input_resolution"][0],
        output_dir=cfg["output_dirs"]["model_comparison"],
    )
