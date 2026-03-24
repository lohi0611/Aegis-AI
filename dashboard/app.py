import os
import time
import csv
import tempfile
from collections import deque
from datetime import datetime

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Intelligence & UI Utils
from ui_utils import apply_custom_css, mission_control_header, kpi_card, navigation_tip
from detect import PPEDetector

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="AegisAI | Safety Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Premium Styling
apply_custom_css()

# ===================== LOGIC CONSTANTS =====================
LOG_CSV = "violations.csv"
SNAP_DIR = "snapshots"
os.makedirs(SNAP_DIR, exist_ok=True)

VIOLATION_CLASSES = {"NO-Hardhat", "NO-Mask", "NO-Safety Vest"}
CSV_HEADER = ["timestamp", "worker_id", "violation_type", "confidence", "x1", "y1", "x2", "y2", "snapshot_path", "status"]

# Ensure CSV header exists
if not os.path.isfile(LOG_CSV):
    with open(LOG_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown('<div class="sidebar-header">🛡️ AEGIS-AI OPERATION</div>', unsafe_allow_html=True)
    st.markdown("*Tactical Monitoring Node: **FAB-NORTH-01***")
    
    st.markdown("---")
    
    st.markdown("### 📡 SENSOR CONFIGURATION")
    video_source = st.selectbox("Intelligence Source", ["Video File", "Webcam (0)"])
    confidence_slider = st.slider("Neural Confidence Threshold", 0.1, 1.0, 0.5, step=0.01)
    
    uploaded_file = None
    if video_source == "Video File":
        uploaded_file = st.file_uploader("Upload Sector Feed", type=["mp4", "avi", "mov"])
    
    use_dshow = st.checkbox("Enhanced Hardware Access (Legacy)", value=True)
    
    st.markdown("---")
    st.markdown("### 🚦 SYSTEM CONTROLS")
    
    if "running" not in st.session_state: st.session_state.running = False
    
    col_c1, col_c2 = st.columns(2)
    if col_c1.button("▶ START SCAN"):
        st.session_state.running = True
        st.session_state.session_rows = []
    if col_c2.button("⏹ STOP SCAN"):
        st.session_state.running = False

    st.markdown("---")
    st.info("💡 **Navigation View:** Use the sidebar menu at the top to switch to Analytics or Compliance Heatmaps.")

# ===================== MAIN HEADER =====================
mission_control_header("AEGIS <span style='color:#4a90e2;'>MISSION CONTROL</span>", 
                      "OPERATIONAL SAFETY INTELLIGENCE & REAL-TIME COMPLIANCE AUDITING")

# ===================== KPI BANNER =====================
col_k1, col_k2, col_k3, col_k4 = st.columns(4)

# Placeholders for KPIs
with col_k1: kpi_frames = st.empty()
with col_k2: kpi_violations = st.empty()
with col_k3: kpi_active = st.empty()
with col_k4: kpi_fps = st.empty()

st.markdown("---")

# ===================== MONITORING GRID =====================
col_left, col_right = st.columns([2.5, 1.2])

with col_left:
    st.markdown('### 💠 Live Optic Array', unsafe_allow_html=True)
    video_ph = st.empty()
    status_ph = st.empty()

with col_right:
    st.markdown('### 📈 Active Intelligence Metrics', unsafe_allow_html=True)
    metrics_chart_ph = st.empty()
    st.markdown('### 🚨 Operational Feed', unsafe_allow_html=True)
    feed_ph = st.container()

# ===================== LOGS & EXPORT =====================
st.markdown("---")
st.markdown('### 📋 Session Intelligence Log', unsafe_allow_html=True)
logs_ph = st.empty()

# Initialization functions
def update_kpis(f, v, a, fps):
    with col_k1: kpi_card("Observations", f, "👁️")
    with col_k2: kpi_card("Violations", v, "🚨", "#ff4b4b")
    with col_k3: kpi_card("Active Alerts", a, "🔔", "#ff9f43")
    with col_k4: kpi_card("System FPS", f"{fps:.1f}", "⚡", "#00d4ff")

# ===================== DETECTION ENGINE =====================
if st.session_state.running:
    detector = PPEDetector(conf=confidence_slider)
    
    # Prep Source
    cap_src = None
    if video_source == "Webcam (0)":
        cap_src = 0
    elif uploaded_file:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]).name
        with open(tmp_file, "wb") as f:
            f.write(uploaded_file.read())
        cap_src = tmp_file
    else:
        st.warning("⚠️ PROMPT REQUIRED: Please define a valid intelligence source.")
        st.session_state.running = False
        st.stop()

    # Open Capture
    if isinstance(cap_src, int) and cap_src == 0 and use_dshow:
        cap = cv2.VideoCapture(cap_src, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(cap_src)
    
    if not cap.isOpened():
        st.error("🚨 SENSOR FAILURE: Unable to access the optic stream.")
        st.session_state.running = False
        st.stop()

    # Global session data
    if "session_rows" not in st.session_state: st.session_state.session_rows = []
    
    prev_time = time.time()
    total_frames = 0
    total_violations = 0
    fps_history = deque(maxlen=60)
    time_history = deque(maxlen=60)

    try:
        while cap.isOpened() and st.session_state.running:
            ret, frame = cap.read()
            if not ret: break

            total_frames += 1
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect
            annotated, detections = detector.detect(rgb)
            
            # Tally
            frame_violations = 0
            rows_to_save = []
            
            for d in detections:
                if d["class_name"] in VIOLATION_CLASSES:
                    frame_violations += 1
                    ts_raw = datetime.now()
                    ts = ts_raw.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Snap path
                    snap_id = f"snap_{ts_raw.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                    snap_path = os.path.join(SNAP_DIR, snap_id)
                    cv2.imwrite(snap_path, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
                    
                    row = [ts, "UNKWN_WKR", d["class_name"], d["confidence"], 
                           *d["bbox"].values(), snap_path, "Violation"]
                    rows_to_save.append(row)
                    st.session_state.session_rows.append(row)

            if rows_to_save:
                with open(LOG_CSV, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(rows_to_save)
                total_violations += len(rows_to_save)

            # Performance Timing
            now = time.time()
            fps = 1.0 / max(1e-6, (now - prev_time))
            prev_time = now
            fps_history.append(fps)
            time_history.append(datetime.now().strftime("%H:%M:%S"))

            # UI Updates
            update_kpis(total_frames, total_violations, frame_violations, fps)
            video_ph.image(annotated, use_container_width=True)
            
            if total_frames % 5 == 0:
                # Metrics Chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(time_history), y=list(fps_history),
                                          mode='lines', name='FPS', line=dict(color='#00d4ff', width=2),
                                          fill='tozeroy', fillcolor='rgba(0, 212, 255, 0.05)'))
                fig.update_layout(
                    height=200, margin=dict(l=0, r=0, t=0, b=0),
                    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
                )
                metrics_chart_ph.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # Feed Update
                with feed_ph:
                    for log in st.session_state.session_rows[-5:]:
                        st.markdown(f'<div style="background:rgba(255, 75, 75, 0.1); border-left: 3px solid #ff4b4b; padding:8px; margin-bottom:5px; font-size:0.8rem;">'
                                    f'🚨 <b>{log[2]}</b> at {log[0].split(" ")[1]}</div>', unsafe_allow_html=True)

                # Logs Update
                if st.session_state.session_rows:
                    logs_ph.dataframe(pd.DataFrame(st.session_state.session_rows, columns=CSV_HEADER).tail(50), 
                                      use_container_width=True)

            time.sleep(0.001)

    finally:
        cap.release()
        st.session_state.running = False
        st.success("✅ MISSION COMPLETED: Sensor stream successfully terminated.")

else:
    update_kpis(0, 0, 0, 0.0)
    video_ph.info("💤 STANDBY MODE: Awaiting tactical command...")
    navigation_tip()
