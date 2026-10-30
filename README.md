# 🛡️ AEGIS — Adaptive Edge Guardian Intelligence for Safety

### **Enterprise AI Safety Intelligence & Real-Time Computer Vision Platform**

*Autonomous PPE Compliance Monitoring, Hazard Mitigation, and Safety Analytics for High-Risk Environments*

<p align="center">
  <a href="https://aegis-ai-bhflqw5bzy8xqxrnuunpkb.streamlit.app/">
    <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Streamlit App">
  </a>
  <a href="https://github.com/lohi0611/Aegis-AI/actions/workflows/ci.yml">
    <img src="https://github.com/lohi0611/Aegis-AI/actions/workflows/ci.yml/badge.svg" alt="CI Tests">
  </a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <a href="https://github.com/ultralytics/ultralytics">
    <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF" alt="YOLOv8">
  </a>
  <a href="https://pytorch.org/">
    <img src="https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?logo=pytorch&logoColor=white" alt="PyTorch">
  </a>
  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  </a>
  <img src="https://img.shields.io/badge/Test_Coverage-66%25-brightgreen" alt="Test Coverage">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  </a>
</p>

<p align="center">
  <strong>
    <a href="https://aegis-ai-bhflqw5bzy8xqxrnuunpkb.streamlit.app/">🌐 Launch Live Cloud Demo</a>
    •
    <a href="#system-architecture">📖 Architecture Documentation</a>
    •
    <a href="#quantitative-empirical-results">📊 Empirical Results</a>
    •
    <a href="#quick-start--installation">🚀 Quick Start</a>
  </strong>
</p>

---

> [!TIP]
> ### 🚀 Live Interactive Cloud Deployment
>
> Try AEGIS directly in your browser:
> **[Launch AEGIS Live Demo](https://aegis-ai-bhflqw5bzy8xqxrnuunpkb.streamlit.app/)**
>
> - **One-Click Demo Mode:** Use the pre-configured demo option on the login screen to explore the platform.
> - **Demo Credentials:** `admin@aegis.ai`
> - **Password:** `Admin@1234`
> - **Role:** Site EHS Director

---

## 📌 Executive Summary

**AEGIS** is an edge-deployable computer vision platform designed for automated Personal Protective Equipment (PPE) compliance monitoring and hazard detection in construction sites and heavy industrial environments.

The platform combines deep neural object detection using **YOLOv8** with a multi-stage stateful compliance engine incorporating:

1. **Spatial Anatomical Association:** Uses bounding-box containment, Intersection over Union (IoU), and centroid proximity to associate safety equipment such as hard hats, safety vests, and face masks with individual workers.

2. **Temporal Hysteresis Filtering:** Implements an N-frame sliding-window confirmation mechanism to reduce transient detection errors caused by occlusions and eliminate unnecessary alerts.

3. **Enterprise Authentication and Persistence:** Implements password hashing using PBKDF2-HMAC-SHA256 and SQLAlchemy-based database logging to maintain user authentication records and safety incident information.

---

## ✨ Key Capabilities & Platform Highlights

| Feature | Description |
|---|---|
| 👁️ **Multi-Modal Video Ingestion** | Supports browser webcams through WebRTC, industrial RTSP/IP camera feeds, and uploaded video files. |
| 🧠 **Fine-Tuned YOLOv8 Detector** | Detects 10 target classes, including PPE equipment and explicit absence indicators such as NO-Hardhat, NO-Safety Vest, and NO-Mask. |
| 📐 **Spatial Association Engine** | Associates detected PPE with individual workers using bounding-box containment, IoU, and anatomical positioning. |
| ⏱️ **Temporal Verification Hysteresis** | Uses multi-frame confirmation to reduce false alerts caused by temporary occlusion and motion blur. |
| 🔐 **Enterprise Authentication & Security** | Provides user authentication, PBKDF2 password hashing, password strength validation, and demo access. |
| 📊 **Safety Analytics & Forensics** | Includes interactive dashboards, compliance scorecards, incident timelines, and snapshot exports. |
| ⚡ **CPU-Based Processing** | Achieves 12.48 FPS at 320 × 320 resolution with an average association latency below 18 ms. |

---

## System Architecture

```text
AEGIS
│
├── Video Sources
│   ├── Camera
│   ├── Video Upload
│   └── RTSP Stream
│       └── VideoProcessor (OpenCV + Frame Buffer)
│
├── Detector Layer
│   └── YOLOv8 (Custom PPE Weights)
│       ├── Person
│       ├── Hardhat
│       ├── NO-Hardhat
│       ├── Safety Vest
│       ├── NO-Safety Vest
│       ├── Mask
│       ├── NO-Mask
│       ├── Safety Cone
│       ├── Machinery
│       └── Vehicle
│
├── src/ — Core Intelligence Layer
│   ├── association/
│   │   └── spatial.py
│   ├── compliance/
│   │   ├── rules.py
│   │   ├── temporal.py
│   │   └── engine.py
│   ├── tracking/
│   ├── alerts/
│   ├── config/
│   ├── database/
│   │   ├── models.py
│   │   └── repository.py
│   ├── video/
│   └── utils/
│
├── evaluation/
│   ├── evaluate_model.py
│   ├── benchmark_realtime.py
│   ├── evaluate_compliance.py
│   ├── error_analysis.py
│   ├── cross_validation.py
│   ├── ablation_study.py
│   ├── compare_models.py
│   └── run_all_evaluations.py
│
├── dashboard/
│   ├── app.py
│   ├── db.py
│   ├── ui_utils.py
│   ├── components/
│   │   ├── landing.py
│   │   └── auth.py
│   └── pages/
│       ├── 1_complianceStats.py
│       └── 2_incidentExplorer.py
│
└── tests/
    ├── test_auth.py
    ├── test_tracking.py
    ├── test_utils.py
    ├── test_metrics.py
    ├── test_association.py
    ├── test_compliance.py
    ├── test_alerts.py
    ├── test_config.py
    └── test_database.py
```

---

## Quantitative Empirical Results

### 1. Object Detection Performance

**Test Split: 82 Images | 760 Instances**

| Class Name | Precision | Recall | F1-Score | mAP@50 | mAP@50-95 |
|---|---:|---:|---:|---:|---:|
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
| **Overall** | **0.9197** | **0.7243** | **0.8104** | **0.8386** | **0.5273** |

---

### 2. Compliance Decision Performance

#### Frame-Level PPE Violation Decision

**Test Images: N = 82**

| Metric | Empirical Value |
|---|---:|
| **Decision Accuracy** | **93.90% (77/82)** |
| **Violation Precision** | **97.78% (44/45)** |
| **Violation Recall / Sensitivity** | **91.67% (44/48)** |
| **Specificity** | **97.06% (33/34)** |
| **Violation F1-Score** | **94.62%** |
| **False Positive Rate (FPR)** | **2.94%** |
| **Missed Hazard Rate (FNR)** | **8.33%** |

#### Worker-Level PPE Compliance Decision

**Ground Truth Workers: N = 174**

| Metric | Empirical Value |
|---|---:|
| **Worker Decision Accuracy** | **74.21%** |
| **Worker Violation Precision** | **83.19%** |
| **Worker Violation Recall** | **75.81%** |
| **Worker Violation F1-Score** | **79.32%** |
| **Worker False Positive Rate (FPR)** | **28.79%** |
| **Worker Missed Hazard Rate (FNR)** | **24.19%** |

---

### 3. CPU Latency & Throughput Benchmark

**Benchmark Duration: 100 Frames**

| Resolution | Mean FPS | Median FPS | Mean Latency (ms) | P95 Latency (ms) | P99 Latency (ms) | RAM (MB) |
|---|---:|---:|---:|---:|---:|---:|
| **640 × 640** | 4.91 | 4.83 | 205.85 | 243.23 | 258.40 | 2758.3 |
| **480 × 480** | 8.17 | 8.42 | 123.44 | 143.67 | 154.20 | 2747.6 |
| **320 × 320** | 12.48 | 12.43 | 81.23 | 95.27 | 104.80 | 2746.0 |

**Operational Observation:** The system demonstrates near-real-time processing on CPU hardware, achieving a throughput of **12.48 FPS at 320 × 320 resolution**.

---

### 4. Error Diagnostics by Object Scale

| Object Scale | Bounding Box Area | GT Count | Detected | Missed | Detection Recall |
|---|---|---:|---:|---:|---:|
| **Small** | Below 32 × 32 px | 328 | 192 | 136 | **58.54%** |
| **Medium** | 32 × 32 to 96 × 96 px | 195 | 160 | 35 | **82.05%** |
| **Large** | Above 96 × 96 px | 237 | 228 | 9 | **96.20%** |

> **Key Operational Limitation:** Small and distant background workers with bounding boxes below 32 × 32 pixels present a significant detection challenge, with a recall of 58.54%. This contributes to the performance difference between frame-level violation detection (93.90%) and worker-level compliance classification (74.21%).

---

## 🚀 Quick Start & Installation

### Prerequisites

- Python 3.10, 3.11, or 3.12
- Git

### Local Setup

**1. Clone the repository**

```bash
git clone https://github.com/lohi0611/Aegis-AI.git
cd Aegis-AI
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r dashboard/requirements.txt
```

### Launching the Application

**Option A: PowerShell Launcher (Windows)**

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

Open your browser and navigate to:

```text
http://localhost:8501
```

---

## 🧪 Testing & Quality Assurance

AEGIS includes an automated Pytest suite designed to validate mathematical metrics, spatial geometry, temporal hysteresis, database persistence, and authentication mechanisms.

### Run Tests

```bash
pytest --cov=src --cov-report=term-missing tests/
```

### Verification Status

- **72/72 Passing Tests**
- **66.21% Code Coverage** across core packages (`src/`)
- CPU-executable automated validation without requiring a GPU

---

## 🔬 Research Evaluation Suite

The project includes standalone evaluation scripts to reproduce model performance and benchmark results.

**1. Object Detection Evaluation**

```bash
python evaluation/evaluate_model.py
```

**2. PPE Compliance Evaluation**

```bash
python evaluation/evaluate_compliance.py
```

**3. CPU Performance Benchmarking**

```bash
python evaluation/benchmark_realtime.py
```

**4. Object Scale Error Analysis**

```bash
python evaluation/error_analysis.py
```

---

## 📂 Project Structure

```text
Aegis-AI/
│
├── .github/
│   └── workflows/              # CI/CD workflows
│
├── configs/
│   └── config.yaml             # System configuration
│
├── dashboard/
│   ├── app.py                  # Main Streamlit application
│   ├── db.py                   # Database and authentication layer
│   ├── ui_utils.py             # UI components and styling
│   ├── components/
│   │   ├── landing.py          # Landing page
│   │   └── auth.py             # Authentication interface
│   ├── pages/
│   │   ├── 1_complianceStats.py
│   │   └── 2_incidentExplorer.py
│   └── requirements.txt
│
├── evaluation/                 # Research evaluation scripts
│
├── src/                        # Core intelligence modules
│   ├── alerts/
│   ├── association/
│   ├── compliance/
│   ├── config/
│   ├── database/
│   ├── tracking/
│   ├── utils/
│   └── video/
│
├── tests/                      # Automated test suite
│
├── app.py                      # Streamlit deployment entry point
└── LICENSE
```

---

## 📜 Citation & Research

If you use AEGIS or its evaluation methodology in academic or industrial research, please cite:

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

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>AEGIS — Making Industrial Workplaces Safer Through AI.</strong>
  <br>
  Built with Python, YOLOv8, PyTorch, OpenCV, SQLAlchemy, and Streamlit.
</p>
