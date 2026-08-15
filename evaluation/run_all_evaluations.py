"""
AEGIS-AI — Master Evaluation & Research Report Generation Suite
Executes all evaluation modules, collects quantitative metrics, and generates
a comprehensive, IEEE-ready experimental results summary report.
"""
import os
import sys
import time
import argparse
from pathlib import Path

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
)
from evaluation.evaluate_model import evaluate_model
from evaluation.benchmark_realtime import benchmark_realtime
from evaluation.evaluate_compliance import evaluate_compliance
from evaluation.error_analysis import run_error_analysis
from evaluation.cross_validation import evaluate_cross_validation_folds
from evaluation.compare_models import compare_models


def generate_markdown_report(all_results: dict, output_file: Path):
    """Generate a formal markdown experimental results report suitable for research analysis."""
    det = all_results.get("detection", {}).get("overall_metrics", {})
    comp = all_results.get("compliance", {}).get("compliance_decision_metrics", {})
    comp_cm = all_results.get("compliance", {}).get("confusion_matrix", {})
    hw = all_results.get("hardware_telemetry", {})
    bench = all_results.get("performance", {}).get("benchmarks_by_resolution", [])

    md_lines = [
        "# Research Evaluation Report",
        "## Real-Time PPE Detection and Compliance Monitoring System for Construction Safety",
        f"**Date/Time Generated:** {all_results.get('timestamp', 'N/A')}  ",
        f"**Hardware Environment:** {hw.get('processor', 'N/A')} | Python {hw.get('python_version', 'N/A')} | PyTorch {hw.get('torch_version', 'N/A')}  ",
        f"**Compute Device:** {all_results.get('device', 'cpu').upper()}  ",
        "",
        "---",
        "",
        "### 1. Executive Quantitative Summary",
        "",
        "| Metric Domain | Metric Name | Value | Percentage / Unit |",
        "|---|---|---|---|",
        f"| **Object Detection** | Precision (mP) | {det.get('precision', 0.0):.4f} | {det.get('precision', 0.0)*100:.2f}% |",
        f"| **Object Detection** | Recall (mR) | {det.get('recall', 0.0):.4f} | {det.get('recall', 0.0)*100:.2f}% |",
        f"| **Object Detection** | F1-Score | {det.get('f1_score', 0.0):.4f} | {det.get('f1_score', 0.0)*100:.2f}% |",
        f"| **Object Detection** | mAP@50 | {det.get('mAP50', 0.0):.4f} | {det.get('mAP50', 0.0)*100:.2f}% |",
        f"| **Object Detection** | mAP@50-95 | {det.get('mAP50_95', 0.0):.4f} | {det.get('mAP50_95', 0.0)*100:.2f}% |",
        f"| **Compliance Engine** | Decision Accuracy | {comp.get('overall_compliance_accuracy', 0.0):.4f} | {comp.get('overall_compliance_accuracy', 0.0)*100:.2f}% |",
        f"| **Compliance Engine** | Violation Precision | {comp.get('violation_precision', 0.0):.4f} | {comp.get('violation_precision', 0.0)*100:.2f}% |",
        f"| **Compliance Engine** | Violation Recall (Sensitivity) | {comp.get('violation_recall_sensitivity', 0.0):.4f} | {comp.get('violation_recall_sensitivity', 0.0)*100:.2f}% |",
        f"| **Compliance Engine** | False Alarm Rate (FPR) | {comp.get('false_positive_rate_fpr', 0.0):.4f} | {comp.get('false_positive_rate_fpr', 0.0)*100:.2f}% |",
        f"| **Compliance Engine** | Missed Hazard Rate (FNR) | {comp.get('false_negative_rate_miss_rate', 0.0):.4f} | {comp.get('false_negative_rate_miss_rate', 0.0)*100:.2f}% |",
        "",
        "---",
        "",
        "### 2. Real-Time Inference Latency & Throughput",
        "",
        "| Resolution | Mean FPS | Median FPS | Mean Latency (ms) | P95 Latency (ms) | Inference Time (ms) | RAM (MB) |",
        "|---|---|---|---|---|---|---|",
    ]

    for b in bench:
        fps_m = b.get("fps_metrics", {})
        lat_m = b.get("latency_metrics_ms", {})
        res_m = b.get("resource_utilization", {})
        md_lines.append(
            f"| {b.get('resolution')} | {fps_m.get('mean_fps', 0):.2f} | {fps_m.get('median_fps', 0):.2f} | "
            f"{lat_m.get('mean_e2e_latency_ms', 0):.2f} | {lat_m.get('p95_e2e_latency_ms', 0):.2f} | "
            f"{lat_m.get('mean_inference_ms', 0):.2f} | {res_m.get('process_ram_mb', 0):.1f} |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "### 3. Compliance Decision Confusion Matrix",
        "",
        f"- **True Positives (Correctly Flagged Violations):** {comp_cm.get('TP_correct_violations', 0)}",
        f"- **False Positives (False Alarms on Compliant Workers):** {comp_cm.get('FP_false_alarms', 0)}",
        f"- **True Negatives (Correctly Verified Compliant Workers):** {comp_cm.get('TN_correct_compliant', 0)}",
        f"- **False Negatives (Critical Missed Hazards):** {comp_cm.get('FN_missed_hazards', 0)}",
        "",
        "---",
        "",
        "### 4. Machine-Readable Result File Index",
        "",
        "- Detection Metrics: `evaluation/results/detection/metrics.json`",
        "- Per-Class Metrics: `evaluation/results/detection/per_class_metrics.csv`",
        "- Performance Benchmarks: `evaluation/results/performance/realtime_benchmark.json`",
        "- Frame-by-Frame Latency: `evaluation/results/performance/realtime_benchmark_frames.csv`",
        "- Compliance Metrics: `evaluation/results/compliance/compliance_metrics.json`",
        "- Per-Violation Metrics: `evaluation/results/compliance/per_violation_compliance.csv`",
        "- Error Diagnostics: `evaluation/results/error_analysis/error_breakdown.json`",
        "- Scale Sensitivity: `evaluation/results/error_analysis/scale_sensitivity.csv`",
        "- Cross-Validation / Splits: `evaluation/results/cross_validation/cross_val_summary.json`",
        "- Model Comparison: `evaluation/results/model_comparison/model_comparison.csv`",
        "",
    ])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[AEGIS-MASTER] Generated formal markdown report at: {output_file}")


def run_all(config_path: str = None, device: str = None):
    """Run full evaluation suite and compile master research report."""
    cfg = load_eval_config(config_path)
    dev = device or cfg["device"]

    print("\n" + "#" * 75)
    print(" STARTING COMPLETE AEGIS-AI RESEARCH EVALUATION SUITE")
    print("#" * 75 + "\n")

    t_start = time.time()
    results = {
        "timestamp": get_hardware_info()["timestamp"],
        "device": dev,
        "hardware_telemetry": get_hardware_info(),
    }

    # 1. Detection Model Evaluation
    print("\n>>> [1/6] Running Object Detection Model Evaluation...")
    results["detection"] = evaluate_model(
        model_path=cfg["model"]["path"],
        data_yaml=cfg["dataset"]["yaml_path"],
        split=cfg["detection_eval"]["split"],
        batch_size=cfg["detection_eval"]["batch_size"],
        imgsz=cfg["model"]["input_resolution"][0],
        device=dev,
        conf_thresh=cfg["model"]["conf_threshold"],
        iou_thresh=cfg["model"]["iou_threshold"],
        output_dir=cfg["output_dirs"]["detection"],
    )

    # 2. Real-Time Performance Benchmark
    print("\n>>> [2/6] Running Real-Time Performance Benchmark...")
    results["performance"] = benchmark_realtime(
        model_path=cfg["model"]["path"],
        resolutions=cfg["benchmark"]["resolutions"],
        num_frames=cfg["benchmark"]["benchmark_frames"],
        warmup_runs=cfg["benchmark"]["warmup_runs"],
        conf_thresh=cfg["model"]["conf_threshold"],
        iou_thresh=cfg["model"]["iou_threshold"],
        device=dev,
        test_video_path=cfg["benchmark"].get("test_video_path"),
        output_dir=cfg["output_dirs"]["performance"],
    )

    # 3. PPE Compliance Decision Evaluation
    print("\n>>> [3/6] Running PPE Compliance Decision Evaluation...")
    split_dir = REPO_ROOT / cfg["dataset"]["splits"][cfg["detection_eval"]["split"]]
    results["compliance"] = evaluate_compliance(
        model_path=cfg["model"]["path"],
        data_split_dir=str(split_dir),
        class_mapping=cfg["dataset"]["classes"],
        conf_thresh=cfg["model"]["conf_threshold"],
        iou_thresh=cfg["model"]["iou_threshold"],
        device=dev,
        output_dir=cfg["output_dirs"]["compliance"],
    )

    # 4. Error Analysis and Diagnostics
    print("\n>>> [4/6] Running Error Analysis and Failure Mode Diagnostics...")
    results["error_analysis"] = run_error_analysis(
        model_path=cfg["model"]["path"],
        data_split_dir=str(split_dir),
        class_mapping=cfg["dataset"]["classes"],
        conf_thresh=cfg["model"]["conf_threshold"],
        iou_thresh=cfg["model"]["iou_threshold"],
        device=dev,
        output_dir=cfg["output_dirs"]["error_analysis"],
    )

    # 5. Cross-Validation & Statistical Aggregation
    print("\n>>> [5/6] Running Cross-Validation & Split Statistical Evaluation...")
    results["cross_validation"] = evaluate_cross_validation_folds(
        device=dev,
        output_dir=cfg["output_dirs"]["cross_validation"],
    )

    # 6. Model Comparison
    print("\n>>> [6/6] Running Model Architecture Comparison...")
    results["model_comparison"] = compare_models(
        data_yaml=cfg["dataset"]["yaml_path"],
        split=cfg["detection_eval"]["split"],
        device=dev,
        imgsz=cfg["model"]["input_resolution"][0],
        output_dir=cfg["output_dirs"]["model_comparison"],
    )

    elapsed_total = round(time.time() - t_start, 2)
    results["total_suite_runtime_seconds"] = elapsed_total

    # Save comprehensive reports
    base_out = Path(cfg["output_dirs"]["base"])
    ensure_dir(base_out)
    
    save_json_report(results, base_out / "comprehensive_summary.json")
    generate_markdown_report(results, base_out / "RESEARCH_EVALUATION_REPORT.md")

    print("\n" + "#" * 75)
    print(f" ALL EVALUATIONS COMPLETED SUCCESSFULLY in {elapsed_total}s!")
    print(f" Reports saved to: {base_out.resolve()}")
    print("#" * 75 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS-AI Run All Evaluations")
    parser.add_argument("--config", type=str, default=None, help="Path to evaluation config YAML")
    parser.add_argument("--device", type=str, default=None, help="Device (cpu or 0)")
    args = parser.parse_args()

    run_all(config_path=args.config, device=args.device)
