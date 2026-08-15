# AEGIS — Adaptive Edge Guardian Intelligence for Safety

> **Real-Time PPE Compliance & Construction Safety Monitoring System**  
> Research-grade implementation for IEEE publication readiness

[![CI Tests](https://github.com/lohi0611/Aegis-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/lohi0611/Aegis-AI/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/detector-YOLOv8-red)](https://github.com/ultralytics/ultralytics)
[![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-ff4b4b)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Abstract

AEGIS is an end-to-end computer vision system for automatic Personal Protective Equipment (PPE) compliance monitoring on construction sites. It integrates a fine-tuned YOLOv8 object detector with a stateful compliance engine combining spatial PPE-to-worker association, temporal hysteresis filtering, and rule-based violation classification. The system demonstrates near-real-time operation on commodity CPU hardware (12.48 FPS at 320×320, 4.91 FPS at 640×640), achieving a multi-class detection **mAP@50 of 0.8386** and **mAP@50-95 of 0.5273** on the Construction Site Safety (CSS) test split. In safety decision evaluation, the system attains **93.90% Frame-Level Violation Decision Accuracy** and **74.21% Worker-Level Compliance Decision Accuracy**. The architecture is designed for empirical reproducibility with an evaluation suite suitable for IEEE conference submission.

---

## System Architecture

```
AEGIS
├── Video Sources (Camera / Video / RTSP Stream)
│   └── VideoProcessor (OpenCV + Frame Buffer)
│
├── Detector Layer
│   └── YOLOv8 (custom PPE weights)
│       Classes: Person, Hardhat, NO-Hardhat,
│                Safety Vest, NO-Safety Vest, Mask, NO-Mask,
│                Safety Cone, Machinery, Vehicle
│
├── src/ — Core Intelligence Layer
│   ├── association/        # Spatial PPE-to-Worker assignment
│   │   └── spatial.py      # Containment + IoU + Anatomical scoring
│   ├── compliance/         # Safety decision pipeline
│   │   ├── rules.py        # PPE requirement rules
│   │   ├── temporal.py     # N-frame confirmation hysteresis
│   │   └── engine.py       # Unified orchestration
│   ├── tracking/           # Centroid/ByteTrack worker track assignment
│   ├── alerts/             # Cooldown-based alert dispatch
│   ├── config/             # YAML + env-var config loader
│   ├── database/           # SQLAlchemy ORM (SQLite / PostgreSQL)
│   │   ├── models.py
│   │   └── repository.py
│   ├── video/              # Frame I/O and preprocessing
│   └── utils/              # Logging, file I/O, telemetry helpers
│
├── evaluation/             # Research Evaluation Suite
│   ├── evaluate_model.py           # YOLO val() detection metrics
│   ├── benchmark_realtime.py       # Latency / FPS / P95 / P99 benchmarks
│   ├── evaluate_compliance.py      # Frame-level & worker-level compliance
│   ├── error_analysis.py           # Scale sensitivity & confusion matrices
│   ├── cross_validation.py         # K-fold dataset cross validation
│   ├── ablation_study.py           # Component ablation (IoU, N-frame)
│   ├── compare_models.py           # Model variant comparison
│   └── run_all_evaluations.py      # Master evaluation runner
│
├── dashboard/              # Streamlit Monitoring Dashboard
│   ├── app.py              # Main entry point
│   └── pages/
│       ├── 1_complianceStats.py    # Analytics + Research tab
│       └── 2_liveMonitor.py        # Real-time video feed
│
└── tests/                  # Unit Test Suite
    ├── test_metrics.py     # Mathematical verification of all metrics
    ├── test_association.py # Spatial geometry and scoring
    ├── test_compliance.py  # Rule engine and hysteresis
    ├── test_alerts.py      # Cooldown and severity routing
    └── test_database.py    # ORM and logging persistence
```

---

## Quantitative Empirical Results

### 1. Object Detection Performance (Test Split, N=82 images, 760 instances)

| Class Name | Precision | Recall | F1-Score | mAP@50 | mAP@50-95 |
|---|---|---|---|---|---|
| **Hardhat** | 0.9936 | 0.8727 | 0.9293 | 0.9425 | 0.6463 |
| **Mask** | 0.9619 | 0.7500 | 0.8428 | 0.8637 | 0.5580 |
| **NO-Hardhat** | 0.8657 | 0.6291 | 0.7287 | 0.7063 | 0.4019 |
| **NO-Mask** | 0.8393 | 0.6709 | 0.7457 | 0.8301 | 0.4144 |
| **NO-Safety Vest** | 0.9378 | 0.7667 | 0.8436 | 0.8762 | 0.5683 |
| **Person** | 0.9592 | 0.8102 | 0.8784 | 0.9006 | 0.5590 |
| **Safety Cone** | 0.8614 | 0.4728 | 0.6105 | 0.6433 | 0.2847 |
| **Safety Vest** | 0.9239 | 0.7958 | 0.8551 | 0.8878 | 0.6203 |
| **Machinery** | 0.9196 | 0.8409 | 0.8785 | 0.8999 | 0.6903 |
| **Vehicle** | 0.9349 | 0.6341 | 0.7557 | 0.8357 | 0.5301 |
| **Overall (All Classes)** | **0.9197** | **0.7243** | **0.8104** | **0.8386** | **0.5273** |

---

### 2. Compliance Decision Performance

#### Frame-Level PPE Violation Decision (N=82 test images)
| Metric | Empirical Value |
|---|---|
| **Decision Accuracy** | **93.90%** (77 / 82 frames) |
| **Violation Precision** | **97.78%** (44 / 45 flags) |
| **Violation Recall / Sensitivity** | **91.67%** (44 / 48 hazard frames) |
| **Specificity** | **97.06%** (33 / 34 clean frames) |
| **Violation F1-Score** | **94.62%** |
| **False Positive Rate (FPR)** | **2.94%** |
| **Missed Hazard Rate (FNR)** | **8.33%** |

#### Worker-Level PPE Compliance Decision (N=174 GT Workers)
| Metric | Empirical Value |
|---|---|
| **Worker Decision Accuracy** | **74.21%** |
| **Worker Violation Precision** | **83.19%** |
| **Worker Violation Recall** | **75.81%** |
| **Worker Violation F1-Score** | **79.32%** |
| **Worker False Positive Rate (FPR)** | **28.79%** |
| **Worker Missed Hazard Rate (FNR)** | **24.19%** |

---

### 3. CPU Latency & Throughput Benchmark (100 frames)

| Resolution | Mean FPS | Median FPS | Mean Latency (ms) | P95 Latency (ms) | P99 Latency (ms) | RAM (MB) |
|---|---|---|---|---|---|---|
| **640 × 640** | 4.91 | 4.83 | 205.85 | 243.23 | 258.40 | 2758.3 |
| **480 × 480** | 8.17 | 8.42 | 123.44 | 143.67 | 154.20 | 2747.6 |
| **320 × 320** | 12.48 | 12.43 | 81.23 | 95.27 | 104.80 | 2746.0 |

*Operational Claim:* The system demonstrates near-real-time operation on commodity CPU hardware, reaching **12.48 FPS at 320×320**.

---

### 4. Error Diagnostics by Object Scale

| Object Scale | Bounding Box Area | GT Count | Detected | Missed | Detection Recall |
|---|---|---|---|---|---|
| **Small** | < 32 × 32 px | 328 | 192 | 136 | **58.54%** |
| **Medium** | 32 × 32 to 96 × 96 px | 195 | 160 | 35 | **82.05%** |
| **Large** | > 96 × 96 px | 237 | 228 | 9 | **96.20%** |

> **Key Operational Limitation:** Distant background workers with sub-32px bounding boxes represent a significant detection challenge (58.54% recall), which explains the performance delta between site-level frame detection (93.90%) and granular worker association (74.21%).

---

## Installation & Usage

### Setup

```bash
# Clone repository
git clone https://github.com/lohi0611/Aegis-AI.git
cd Aegis-AI

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows (or source .venv/bin/activate on Linux)

# Install dependencies
pip install -r requirements.txt
```

### Launch Dashboard

```bash
streamlit run dashboard/app.py
```

### Run Evaluation Suite

```bash
# Run detection evaluation
python evaluation/evaluate_model.py

# Run compliance evaluation (frame-level and worker-level)
python evaluation/evaluate_compliance.py

# Run latency benchmark
python evaluation/benchmark_realtime.py

# Run error analysis
python evaluation/error_analysis.py
```

### Run Unit Tests (No GPU Required)

```bash
pytest tests/ -v
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
