<div align="center">

# 🛡️ AEGIS — Adaptive Edge Guardian Intelligence for Safety

### **Enterprise AI Safety Intelligence & Real-Time Computer Vision Platform**
*Autonomous PPE Compliance Monitoring, Hazard Mitigation, and Safety Analytics for High-Risk Environments*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aegis-ai.streamlit.app/)
[![CI Tests](https://github.com/lohi0611/Aegis-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/lohi0611/Aegis-AI/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://github.com/ultralytics/ultralytics)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit_1.55-FF4B4B.svg?logo=streamlit&logoColor=white)](https://aegis-ai.streamlit.app/)
[![Test Coverage](https://img.shields.io/badge/Test_Coverage-66%25-brightgreen.svg)](#-testing--quality-assurance)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<br/>

**[🌐 Launch Live Cloud Demo](https://aegis-ai.streamlit.app/)** • **[📖 Architecture Documentation](#-system-architecture)** • **[📊 Empirical Results](#-quantitative-empirical-results)** • **[🚀 Quick Start](#-quick-start--installation)**

---

</div>

> [!TIP]
> ### 🚀 Live Interactive Cloud Deployment
> **Try AEGIS directly in your browser:** **[https://aegis-ai.streamlit.app](https://aegis-ai.streamlit.app/)**
> 
> * **⚡ One-Click Demo Mode:** Click the pre-configured demo button on the login screen to explore with full administrative privileges.
> * **Default Credentials:** `admin@aegis.ai` &nbsp;|&nbsp; Password: `Admin@1234` &nbsp;|&nbsp; Role: *Site EHS Director*

---

## 📌 Executive Summary

**AEGIS** is an enterprise-ready, edge-deployable computer vision platform engineered for automated Personal Protective Equipment (PPE) compliance monitoring and hazard detection on construction sites and heavy industrial facilities. 

Designed for IEEE-grade empirical validation and field deployment, AEGIS bridges deep neural object detection (**YOLOv8**) with a multi-stage **stateful compliance engine** incorporating:
1. **Spatial Anatomical Association:** Multi-metric containment, IoU, and centroid proximity assignment connecting safety gear (hard hats, high-vis vests, face masks) to individual tracked workers.
2. **Temporal Hysteresis Filtering:** Sliding-window $N$-frame confirmation buffer to suppress transient occlusions and eliminate false-positive alerts.
3. **Enterprise RBAC & Persistence:** Cryptographic user authentication (PBKDF2-HMAC-SHA256) and SQLAlchemy ORM audit logging for regulatory compliance (OSHA / ISO 45001).

---

## ✨ Key Capabilities & Platform Highlights

| Feature | Description |
| :--- | :--- |
| 👁️ **Multi-Modal Video Ingestion** | Real-time browser webcams via WebRTC, industrial RTSP/IP camera feeds, and video file upload analysis. |
| 🧠 **Fine-Tuned YOLOv8 Detector** | 10 target classes including gear presence and explicit absence indicators (*NO-Hardhat*, *NO-Safety Vest*, *NO-Mask*). |
| 📐 **Spatial Association Engine** | Anatomical bounding-box heuristics assigning gear to worker torsos and heads with custom containment thresholds. |
| ⏱️ **Temporal Verification Hysteresis** | Multi-frame persistence buffer preventing false alarms from brief motion blur or line-of-sight obstruction. |
| 🔐 **Enterprise Auth & Security** | Split-screen SaaS authentication with PBKDF2 salted password hashing, live password strength meter, and demo sandbox. |
| 📊 **Safety Analytics & Forensics** | Interactive Plotly dashboards, compliance scorecards, incident timeline explorer, and automated snapshot exports. |
| ⚡ **Near-Real-Time Edge Throughput** | Highly optimized CPU pipeline achieving **12.48 FPS at 320×320** and sub-18ms association latency on standard compute. |

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
├── dashboard/              # Enterprise Streamlit SaaS Application
│   ├── app.py              # Multi-source vision engine & router
│   ├── db.py               # Data layer bridge & user auth wrapper
│   ├── ui_utils.py         # Design tokens, CSS system, and executive navbars
│   ├── components/
│   │   ├── landing.py      # SaaS landing page with live interactive preview
│   │   └── auth.py         # Split-screen PBKDF2 authentication & demo mode
│   └── pages/
│       ├── 1_complianceStats.py    # Analytics & OSHA compliance telemetry
│       └── 2_incidentExplorer.py   # Incident forensics & audit vault
│
└── tests/                  # Automated Pytest Suite (72 tests, 66% coverage)
    ├── test_auth.py        # PBKDF2 cryptography & User model mapping
    ├── test_tracking.py    # Centroid distance association & track lifecycle
    ├── test_utils.py       # Performance timers, latency & logging
    ├── test_metrics.py     # Mathematical verification of all metrics
    ├── test_association.py # Spatial geometry, IoU, and anatomical scoring
    ├── test_compliance.py  # Rule engine & temporal confirmation hysteresis
    ├── test_alerts.py      # Cooldown and severity routing
    ├── test_config.py      # Dynamic configuration loading
    └── test_database.py    # SQLAlchemy ORM and incident logging persistence
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

## 🚀 Quick Start & Installation

### Prerequisites
* Python 3.10, 3.11, or 3.12
* Git

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/lohi0611/Aegis-AI.git
cd Aegis-AI

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r dashboard/requirements.txt
```

### Launching the Application

**Option A: PowerShell One-Click Launcher (Windows)**
```powershell
.\Run_SafetyEye.ps1
```

**Option B: Batch Launcher (Windows CMD)**
```cmd
run_app.bat
```

**Option C: Standard Streamlit Command**
```bash
streamlit run app.py
```
Then navigate to **`http://localhost:8501`** in your browser.

---

## 🧪 Testing & Quality Assurance

AEGIS includes an automated unit test suite verifying mathematical metrics, spatial geometry, temporal hysteresis, database persistence, and cryptographic authentication.

```bash
# Run the complete test suite with coverage report
pytest --cov=src --cov-report=term-missing tests/
```

### Verification Status:
* **72 / 72 Passing Tests** (0 failures, 0 regressions)
* **66.21% Code Coverage** across all core packages (`src/`)
* Completely CPU-executable — zero GPU required for automated validation

---

## 🔬 Research Evaluation Suite

Reproduce IEEE paper benchmark metrics using the standalone evaluation scripts:

```bash
# Run YOLOv8 detection mAP@50 and mAP@50-95 evaluation
python evaluation/evaluate_model.py

# Run frame-level and worker-level safety compliance decision evaluation
python evaluation/evaluate_compliance.py

# Benchmark CPU latency, FPS, P95/P99 percentiles, and memory footprint
python evaluation/benchmark_realtime.py

# Run object scale sensitivity and spatial error diagnostics
python evaluation/error_analysis.py
```

---

## 📂 Project Structure

```
Aegis-AI/
├── .github/workflows/          # CI/CD automated test & build workflows
├── configs/
│   └── config.yaml             # System & detector configuration parameters
├── dashboard/                  # Production Streamlit SaaS application
│   ├── app.py                  # Main dashboard orchestrator & video engine
│   ├── db.py                   # Data access layer & auth wrapper
│   ├── ui_utils.py             # Design system, CSS tokens, and navbars
│   ├── components/
│   │   ├── landing.py          # Enterprise SaaS landing page
│   │   └── auth.py             # Split-screen login / signup & demo mode
│   ├── pages/
│   │   ├── 1_complianceStats.py# Historical compliance analytics
│   │   └── 2_incidentExplorer.py# Forensic incident snapshot browser
│   └── requirements.txt        # Dashboard runtime dependencies
├── evaluation/                 # Research evaluation & empirical benchmark suite
├── src/                        # Core algorithmic package
│   ├── alerts/                 # Cooldown notification manager
│   ├── association/            # Spatial worker-PPE association
│   ├── compliance/             # Rules & temporal hysteresis engine
│   ├── config/                 # Dynamic YAML configuration loader
│   ├── database/               # SQLAlchemy ORM models & repository
│   ├── tracking/               # Centroid tracker implementation
│   ├── utils/                  # Telemetry & logger utilities
│   └── video/                  # Video stream processor
├── tests/                      # Pytest unit test suite (72 tests)
├── app.py                      # Root deployment forwarder for Streamlit Cloud
└── LICENSE                     # MIT License
```

---

## 📜 Citation & Research

If you utilize AEGIS or its evaluation methodology in academic or industrial research, please cite:

```bibtex
@article{aegis_safety_2026,
  title={AEGIS: Adaptive Edge Guardian Intelligence for Real-Time PPE Compliance and Construction Safety Monitoring},
  author={Siddamreddy, Lohitha and Contributors},
  journal={arXiv preprint},
  year={2026}
}
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
