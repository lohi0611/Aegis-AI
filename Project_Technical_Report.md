# Real-Time PPE Detection and Compliance Monitoring System for Construction Safety
## Technical & Research Evaluation Report

---

## 1. Abstract
Automated compliance monitoring of Personal Protective Equipment (PPE) is critical for mitigating occupational fatalities and injuries in construction environments. This report documents the architecture, experimental evaluation, and empirical validation of **AEGIS-AI**, an end-to-end computer vision and rule-based safety monitoring system. The framework integrates a fine-tuned **YOLOv8** object detector, a spatial person-to-PPE association module, an automated **Centroid Tracking** algorithm with temporal cooldown deduplication, an industrial **Streamlit** command-center dashboard, a persistent **SQLAlchemy/SQLite** relational logging layer, and a dedicated **Evaluation & Diagnostics Suite**. Evaluated across the Construction Site Safety (CSS) benchmark, the system achieves **0.8386 mAP@50** and **0.5273 mAP@50-95** in multi-class object detection. In safety decision evaluation, the system attains **93.90% Frame-Level PPE Violation Decision Accuracy** (97.78% Precision, 91.67% Recall, 2.94% FPR on $N=82$ test frames) and **74.21% Worker-Level PPE Compliance Decision Accuracy** (83.19% Precision, 75.81% Recall, 28.79% FPR across $N=190$ evaluated worker decisions derived from 174 ground-truth workers). Empirical latency scaling on commodity CPU hardware ranges from **205.85 ms (4.91 FPS)** at 640×640 to **81.23 ms (12.48 FPS)** at 320×320.

---

## 2. System Architecture & Methodology

```
                   [ Input Video Stream / Webcam ]
                                  │
                                  ▼
                   [ Frame Acquisition & Preprocessing ]
                                  │
                                  ▼
                   [ YOLOv8 Deep Object Detection ]
                     (Hardhat, Vest, Mask, Person)
                                  │
                                  ▼
                   [ Spatial Person-PPE Association ]
                     (Containment, IoU, Anatomy Priors)
                                  │
                                  ▼
                   [ Centroid Tracking & Association ]
                     (Persistent Worker IDs: WKR_101)
                                  │
                                  ▼
                   [ Rule-Based Compliance Engine ]
                     (Temporal 15s Event Cooldown)
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       [ Persistent DB Logging ]        [ Live Command Center ]
       (Sessions, Violations)          (Real-Time Alerts, KPIs)
                  │
                  ▼
    =======================================================
               RESEARCH & EVALUATION LAYER
    =======================================================
       │                  │                  │
       ▼                  ▼                  ▼
 [ Detection ]     [ Performance ]    [ Compliance ]
 (P, R, mAP50,     (FPS, Latency,     (Frame-Level &
  mAP50-95, CM)     P95, P99, RAM)     Worker-Level)
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                 [ Error Diagnostics & Ablation ]
                 (Scale, Confusions, A0-A4)
```

---

## 3. Empirical Experimental Results

### 3.1 Object Detection Performance (Test Split, N=82 images, 760 ground-truth instances)

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

### 3.2 Compliance Decision Engine Performance

A strict methodological distinction is made between **Frame-Level Violation Decisions** (site alarm activation) and **Worker-Level PPE Compliance Decisions** (individual worker state estimation).

#### 3.2.1 Frame-Level PPE Violation Decision Performance (N=82 test images)
Evaluates whether the system correctly detects the presence of any safety hazard in the camera field of view.

| Metric Name | Formula / Derivation | Empirical Value | Percentage |
|---|---|---|---|
| **Frame-Level Decision Accuracy** | (TP + TN) / Total | 0.9390 | **93.90%** |
| **Violation Precision (PPV)** | TP / (TP + FP) | 0.9778 | **97.78%** |
| **Violation Recall / Sensitivity (TPR)** | TP / (TP + FN) | 0.9167 | **91.67%** |
| **Frame-Level Specificity (TNR)** | TN / (TN + FP) | 0.9706 | **97.06%** |
| **Violation F1-Score** | 2·P·R / (P + R) | 0.9462 | **94.62%** |
| **False Positive Rate (False Alarm Rate)** | FP / (FP + TN) | 0.0294 | **2.94%** |
| **False Negative Rate (Missed Hazard Rate)** | FN / (TP + FN) | 0.0833 | **8.33%** |

**Frame-Level Confusion Matrix (N = 82):**
- **True Positives (Correctly Flagged Hazard Frames):** 44
- **False Positives (False Alarms on Clean Frames):** 1
- **True Negatives (Correctly Verified Clean Frames):** 33
- **False Negatives (Missed Hazard Frames):** 4

---

#### 3.2.2 Worker-Level PPE Compliance Decision Performance
Evaluates individual worker compliance by performing spatial person-to-PPE containment and anatomical association, followed by policy rule evaluation.

**Accounting & Decision Cardinality:**
- **Unique Ground-Truth Workers Annotated:** 174
- **Total Predicted Workers by Model:** 160
- **Matched Worker Pairs (IoU $\ge$ 0.50):** 144
- **Unmatched Ground-Truth Workers (Missed Person Detections):** 30
- **Unmatched Predicted Workers (Spurious Person Detections):** 16
- **Total Evaluated Worker Decisions ($174 + 16$):** **190**

| Metric Name | Formula / Derivation | Empirical Value | Percentage |
|---|---|---|---|
| **Worker Compliance Decision Accuracy** | (TP + TN) / Total Decisions | 0.7421 | **74.21%** (141 / 190) |
| **Worker Violation Precision (PPV)** | TP / (TP + FP) | 0.8319 | **83.19%** (94 / 113) |
| **Worker Violation Recall / Sensitivity (TPR)** | TP / (TP + FN) | 0.7581 | **75.81%** (94 / 124) |
| **Worker Specificity (TNR)** | TN / (TN + FP) | 0.7121 | **71.21%** (47 / 66) |
| **Worker Violation F1-Score** | 2·P·R / (P + R) | 0.7932 | **79.32%** |
| **Worker False Positive Rate (FPR)** | FP / (FP + TN) | 0.2879 | **28.79%** (19 / 66) |
| **Worker False Negative Rate (FNR)** | FN / (TP + FN) | 0.2419 | **24.19%** (30 / 124) |

**Worker-Level Confusion Matrix (N = 190 Decisions):**
- **True Positives (Correct Worker Violations):** 94
- **False Positives (Compliant Workers Flagged as Violations + Spurious False Alarms):** 19 ($4 \text{ matched} + 15 \text{ spurious}$)
- **True Negatives (Compliant Workers Verified):** 47 ($43 \text{ matched} + 3 \text{ unmatched GT} + 1 \text{ spurious}$)
- **False Negatives (Missed Worker Violations):** 30 ($3 \text{ matched} + 27 \text{ missed GT persons}$)

---

### 3.3 Component Ablation Study (A0 through A4)

To quantify the exact marginal contribution of each architectural module, a systematic 5-tier ablation experiment was executed across the annotated test split and continuous sequential video stream:

| Configuration | Architectural Components | Evaluation Scope | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | FPR (%) | Mean Latency (ms) | P95 Latency (ms) | FPS | Generated Events (100 frames) | Alert Reduction vs A0 (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A0: Base Detector Only** | YOLOv8n (Direct Negative Class Thresholding) | Frame-Level Alarm | 93.90 | 97.78 | 91.67 | 94.63 | 2.94 | 270.15 | 386.33 | 3.70 | 51 | 0.0% (Baseline) |
| **A1: + Spatial Association** | Detector + Spatial Containment & Anatomy Rules | Worker-Level State | 74.21 | 83.19 | 75.81 | 79.33 | 28.79 | 270.41 | 386.41 | 3.70 | 224 | N/A (Granular Worker) |
| **A2: + Centroid Tracking** | Detector + Spatial + Centroid Track IDs | Tracked Worker Stream | 74.21 | 83.19 | 75.81 | 79.33 | 28.79 | 197.58 | 286.27 | 5.06 | 224 | N/A (Identity Preserved) |
| **A3: + Temporal Hysteresis** | Detector + Spatial + Tracking + N=3 Confirm | Confirmed Violations | 74.21 | 83.19 | 75.81 | 79.33 | 28.79 | 197.60 | 286.32 | 5.06 | 222 | 0.89% (Flicker Suppressed) |
| **A4: Full AEGIS Pipeline** | Complete Pipeline + 5s Alert Cooldown | Actionable Dispatches | 74.21 | 83.19 | 75.81 | 79.33 | 28.79 | 197.55 | 286.22 | 5.06 | **21** | **58.82% Alert Flooding Reduction** |

**Key Ablation Insights:**
1. **Spatial Association Value (A0 $\rightarrow$ A1):** Moves safety monitoring from coarse camera-level flags to individual worker identity and per-worker violation attribution.
2. **Computational Overhead:** The spatial association and centroid tracking stages add $<1.5\text{ ms}$ overhead to the neural inference pass.
3. **Alert Flooding Suppression (A1/A2 $\rightarrow$ A4):** While per-frame worker evaluation generates 224 violation instances across multi-person scenes, temporal hysteresis and cooldown throttling suppress repeated notifications down to **21 actionable, stabilized alerts** (a **58.82% reduction** compared to raw detector frame events, and **90.62% reduction** compared to raw per-frame worker violations).

---

### 3.4 Real-Time Throughput & Latency Profiling

Evaluated empirically over 100 consecutive frames on commodity multi-core CPU hardware (Intel Core i5, single-stream CPU execution, batch size = 1):

| Input Resolution | Mean FPS | Median FPS | Std FPS | Mean Latency (ms) | P95 Latency (ms) | P99 Latency (ms) | Preprocess (ms) | Inference (ms) | Postprocess (ms) | Process RAM (MB) |
|---|---|---|---|---|---|---|---|---|---|---|
| **640 × 640** | 4.91 | 4.83 | 0.28 | 205.85 | 243.23 | 258.40 | 2.14 | 198.87 | 1.34 | 2758.3 |
| **480 × 480** | 8.17 | 8.42 | 0.45 | 123.44 | 143.67 | 154.20 | 1.82 | 118.44 | 1.22 | 2747.6 |
| **320 × 320** | 12.48 | 12.43 | 0.52 | 81.23 | 95.27 | 104.80 | 1.55 | 77.88 | 1.15 | 2746.0 |

*Operational Claim:* The system demonstrates near-real-time operation on commodity multi-core CPU hardware, reaching **12.48 FPS at 320×320** input resolution and **4.91 FPS at 640×640** resolution.

---

### 3.5 Failure Mode & Error Analysis

#### Detection Recall by Object Scale
- **Small Objects (< 32×32 px):** 58.54% Recall (192 / 328 detected, 136 missed)
- **Medium Objects (32×96 px):** 82.05% Recall (160 / 195 detected, 35 missed)
- **Large Objects (> 96×96 px):** 96.20% Recall (228 / 237 detected, 9 missed)

**Diagnostic Insight & Limitation:**
1. **Scale Bottleneck:** Missed detections are overwhelmingly concentrated in small, distant background workers (sub-32px scale), where recall drops to **58.54%**. 
2. **Resolution Sensitivity:** For medium-scale objects (32×96 px), detection recall is **82.05%**, while large foreground objects (>96px) reach **96.20%**.
3. **Performance Delta:** The lower recall on small PPE bounding boxes is the primary cause for the delta between frame-level decision accuracy (93.90%) and granular worker-level compliance decision accuracy (74.21%).
4. **Site Camera Deployment Recommendation:** Surveillance cameras should be positioned at mounting heights that ensure worker bounding boxes exceed 64×64 pixels in the monitored danger zone.

---

## 4. IEEE Paper Readiness Assessment

### ✅ READY (Empirical Evidence Established)
1. **Object Detection Efficacy**: Precision (0.9197), Recall (0.7243), mAP@50 (0.8386), mAP@50-95 (0.5273) on the 10-class CSS test split.
2. **Methodological Rigor & Accurate Accounting**: Explicit mathematical separation and empirical reporting of Frame-Level decisions (93.90% accuracy, $N=82$) vs. Worker-Level decisions (74.21% accuracy, $N=190$ decisions from 174 GT workers).
3. **Systematic Component Ablation**: Complete A0 $\rightarrow$ A4 ablation study measuring marginal latency and alert reduction (58.82% suppression of event flooding).
4. **Reproducible Experimental Architecture**: Standardized CLI tools (`evaluation/evaluate_model.py`, `evaluate_compliance.py`, `ablation_study.py`, `benchmark_realtime.py`, `error_analysis.py`).
5. **Latency Profiling**: Frame-by-frame measured latency distributions with Mean, Median, P95, and P99 metrics across multiple input resolutions.
6. **Scale Sensitivity Analysis**: Empirical breakdown demonstrating that 75.5% of misses occur on small sub-32px scale objects.

### ⚠️ NEEDS EXPERIMENT (Further Work Required)
1. **Multi-Camera Scalability**: Benchmarking simultaneous multi-RTSP camera stream synchronization on edge servers.
2. **Adverse Weather / Extreme Occlusion**: Stratified evaluation on extreme rain/fog/night conditions (requires curated dataset expansion).
3. **Hardware Acceleration Benchmark**: Running formal benchmarks on dedicated edge accelerators (NVIDIA Jetson Orin / RTX GPUs).

### 📚 NEEDS LITERATURE REVIEW
1. Comparison against recent published 2023–2025 PPE papers (e.g., YOLOv7-Tiny, RT-DETR, Faster R-CNN on SHWD and Pictor-v3 datasets).
2. Theoretical discussion on spatial association vs direct negative class labeling (`NO-Hardhat`).

### 🚫 DO NOT CLAIM (Scientifically Unsupported)
- Do **NOT** claim *"100% safety violation prevention"* or *"zero false alarms"*.
- Do **NOT** claim *"30+ FPS on CPU"* — the CPU benchmark measures 12.48 FPS at 320x320 and 4.91 FPS at 640x640.
- Do **NOT** claim *"GPU acceleration of 60 FPS"* unless a physical GPU benchmark run is recorded.
- Do **NOT** claim *"100% reduction in manual inspection costs"* without conducting an industrial human-subject study.
- Do **NOT** describe medium-scale detection as ">90%" — the empirical measurement is **82.05%**.
