"""
AEGIS-AI — Real-Time Inference Performance Benchmark
Accurately benchmarks inference latency (preprocess, forward-pass, NMS postprocess),
end-to-end throughput (FPS), hardware utilization, and resolution scaling.
Computes Mean, Median, Std, Min, Max, and 95th percentile metrics over N frames.
"""
import os
import sys
import time
import argparse
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import psutil
import torch
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


def benchmark_realtime(
    model_path: str,
    resolutions: list = None,
    num_frames: int = 100,
    warmup_runs: int = 10,
    conf_thresh: float = 0.25,
    iou_thresh: float = 0.45,
    device: str = "cpu",
    test_video_path: str = None,
    output_dir: str = "evaluation/results/performance",
) -> dict:
    """
    Run empirical real-time benchmarking for YOLOv8 PPE detection.
    """
    if resolutions is None:
        resolutions = [[640, 640], [480, 480], [320, 320]]

    out_path = Path(output_dir)
    ensure_dir(out_path)

    print(f"\n=================================================================")
    print(f" AEGIS-AI: Real-Time Performance & Latency Benchmark")
    print(f" Model:       {model_path}")
    print(f" Device:      {device}")
    print(f" Benchmark:   {num_frames} frames (Warmup: {warmup_runs} frames)")
    print(f" Resolutions: {resolutions}")
    print(f"=================================================================\n")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model weights not found at: {model_path}")

    model = YOLO(model_path)

    # Prepare input frames (from sample video or synthetic construction frame)
    sample_frames = []
    if test_video_path and os.path.exists(test_video_path):
        cap = cv2.VideoCapture(test_video_path)
        while cap.isOpened() and len(sample_frames) < num_frames:
            ret, f = cap.read()
            if not ret:
                break
            sample_frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        cap.release()

    if not sample_frames:
        # Fallback to test dataset images or synthetic frame
        test_img_dir = REPO_ROOT / "infosys" / "dataset" / "css-data" / "test" / "images"
        if test_img_dir.exists():
            img_files = list(test_img_dir.glob("*.jpg")) + list(test_img_dir.glob("*.png"))
            for p in img_files[:num_frames]:
                img = cv2.imread(str(p))
                if img is not None:
                    sample_frames.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    if not sample_frames:
        # Synthetic fallback
        sample_frames = [np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8) for _ in range(num_frames)]

    # Cycle sample frames up to num_frames
    while len(sample_frames) < num_frames:
        sample_frames.extend(sample_frames[:num_frames - len(sample_frames)])
    sample_frames = sample_frames[:num_frames]

    resolution_results = []
    detailed_frame_records = []

    # Process metrics
    process = psutil.Process(os.getpid())

    for res in resolutions:
        w, h = res
        imgsz = max(w, h)
        print(f"--> Benchmarking Resolution: {w}x{h} (imgsz={imgsz})...")

        # Warmup runs
        for _ in range(warmup_runs):
            _ = model.predict(sample_frames[0], imgsz=imgsz, conf=conf_thresh, iou=iou_thresh, device=device, verbose=False)

        latencies_e2e = []
        preprocess_times = []
        inference_times = []
        postprocess_times = []
        cpu_usage_samples = []

        for idx, frame in enumerate(sample_frames):
            # Track CPU start
            cpu_before = psutil.cpu_percent(interval=None)

            # High precision timing
            t_start = time.perf_counter()
            results = model.predict(frame, imgsz=imgsz, conf=conf_thresh, iou=iou_thresh, device=device, verbose=False)
            t_end = time.perf_counter()

            e2e_ms = (t_end - t_start) * 1000.0
            latencies_e2e.append(e2e_ms)

            # Ultralytics internal breakdown if available
            speed = results[0].speed
            prep_ms = speed.get("preprocess", 0.0)
            inf_ms = speed.get("inference", e2e_ms)
            post_ms = speed.get("postprocess", 0.0)

            preprocess_times.append(prep_ms)
            inference_times.append(inf_ms)
            postprocess_times.append(post_ms)

            cpu_usage_samples.append(psutil.cpu_percent(interval=None))

            detailed_frame_records.append({
                "resolution": f"{w}x{h}",
                "frame_id": idx + 1,
                "e2e_latency_ms": round(e2e_ms, 3),
                "preprocess_ms": round(prep_ms, 3),
                "inference_ms": round(inf_ms, 3),
                "postprocess_ms": round(post_ms, 3),
                "fps": round(1000.0 / max(1e-3, e2e_ms), 2),
            })

        latencies = np.array(latencies_e2e)
        fps_array = 1000.0 / latencies

        mem_info = process.memory_info()
        ram_mb = round(mem_info.rss / (1024 * 1024), 2)

        res_summary = {
            "resolution": f"{w}x{h}",
            "input_dimension": [w, h],
            "num_evaluated_frames": num_frames,
            "fps_metrics": {
                "mean_fps": round(float(np.mean(fps_array)), 2),
                "median_fps": round(float(np.median(fps_array)), 2),
                "std_fps": round(float(np.std(fps_array)), 2),
                "min_fps": round(float(np.min(fps_array)), 2),
                "max_fps": round(float(np.max(fps_array)), 2),
            },
            "latency_metrics_ms": {
                "mean_e2e_latency_ms": round(float(np.mean(latencies)), 2),
                "median_e2e_latency_ms": round(float(np.median(latencies)), 2),
                "std_e2e_latency_ms": round(float(np.std(latencies)), 2),
                "p95_e2e_latency_ms": round(float(np.percentile(latencies, 95)), 2),
                "min_e2e_latency_ms": round(float(np.min(latencies)), 2),
                "max_e2e_latency_ms": round(float(np.max(latencies)), 2),
                "mean_preprocess_ms": round(float(np.mean(preprocess_times)), 2),
                "mean_inference_ms": round(float(np.mean(inference_times)), 2),
                "mean_postprocess_ms": round(float(np.mean(postprocess_times)), 2),
            },
            "resource_utilization": {
                "mean_cpu_percent": round(float(np.mean(cpu_usage_samples)), 2),
                "process_ram_mb": ram_mb,
            }
        }
        resolution_results.append(res_summary)

    # Master benchmark report
    benchmark_report = {
        "experiment": "Real-Time Inference Performance Benchmark",
        "timestamp": get_hardware_info()["timestamp"],
        "model": str(model_path),
        "device": device,
        "conf_threshold": conf_thresh,
        "iou_threshold": iou_thresh,
        "hardware_telemetry": get_hardware_info(),
        "benchmarks_by_resolution": resolution_results,
    }

    # Save outputs
    save_json_report(benchmark_report, out_path / "realtime_benchmark.json")
    save_csv_report(pd.DataFrame(detailed_frame_records), out_path / "realtime_benchmark_frames.csv")
    
    # Save resolution comparison summary CSV
    summary_rows = []
    for r in resolution_results:
        summary_rows.append({
            "Resolution": r["resolution"],
            "Mean FPS": r["fps_metrics"]["mean_fps"],
            "Median FPS": r["fps_metrics"]["median_fps"],
            "Std FPS": r["fps_metrics"]["std_fps"],
            "Mean Latency (ms)": r["latency_metrics_ms"]["mean_e2e_latency_ms"],
            "P95 Latency (ms)": r["latency_metrics_ms"]["p95_e2e_latency_ms"],
            "Inference (ms)": r["latency_metrics_ms"]["mean_inference_ms"],
            "RAM (MB)": r["resource_utilization"]["process_ram_mb"],
        })
    save_csv_report(pd.DataFrame(summary_rows), out_path / "realtime_benchmark_summary.csv")

    # Print clean summary
    print("\n" + "=" * 75)
    print(" REAL-TIME INFERENCE BENCHMARK SUMMARY")
    print("=" * 75)
    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))
    print("=" * 75 + "\n")

    return benchmark_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS-AI Real-Time Inference Performance Benchmark")
    parser.add_argument("--config", type=str, default=None, help="Path to evaluation config YAML")
    parser.add_argument("--frames", type=int, default=100, help="Number of benchmark frames")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or 0)")
    args = parser.parse_args()

    cfg = load_eval_config(args.config)
    
    benchmark_realtime(
        model_path=cfg["model"]["path"],
        resolutions=cfg["benchmark"]["resolutions"],
        num_frames=args.frames or cfg["benchmark"]["benchmark_frames"],
        warmup_runs=cfg["benchmark"]["warmup_runs"],
        conf_thresh=cfg["model"]["conf_threshold"],
        iou_thresh=cfg["model"]["iou_threshold"],
        device=args.device or cfg["device"],
        test_video_path=cfg["benchmark"].get("test_video_path"),
        output_dir=cfg["output_dirs"]["performance"],
    )
