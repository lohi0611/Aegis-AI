import os
import time
import csv
import tempfile
import random
from collections import deque
from datetime import datetime

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Intelligence & UI Utils
from ui_utils import apply_custom_css, mission_control_header, kpi_card, draw_incident_card, navigation_tip
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

# ===================== ABSOLUTE PATH RESOLUTION =====================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

LOG_CSV = os.path.join(project_root, "violations.csv")
SNAP_DIR = os.path.join(project_root, "snapshots")
os.makedirs(SNAP_DIR, exist_ok=True)

# Find Sample Video
sample_video_paths = [
    os.path.join(current_dir, "uploaded_video.mp4"),
    os.path.join(project_root, "uploaded_video.mp4"),
    "uploaded_video.mp4"
]
sample_video = None
for p in sample_video_paths:
    if os.path.exists(p):
        sample_video = p
        break

VIOLATION_CLASSES = ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
ALL_CLASSES = ["Hardhat", "Mask", "NO-Hardhat", "NO-Mask", "NO-Safety Vest", "Person", "Safety Cone", "Safety Vest", "Machinery", "Vehicle"]
CSV_HEADER = ["timestamp", "worker_id", "violation_type", "confidence", "x1", "y1", "x2", "y2", "snapshot_path", "status"]

# Ensure CSV header exists
if not os.path.isfile(LOG_CSV):
    with open(LOG_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown('<div style="text-align: center; margin-bottom: 20px;"><span style="font-size: 2.2rem; filter: drop-shadow(0 0 10px rgba(88, 166, 255, 0.35));">🛡️</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.3rem; font-weight: 800; color: #ffffff; text-align: center; letter-spacing: 2px; margin-bottom: 5px;">AEGIS-AI</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); text-align: center; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 25px;">Tactical Monitoring Node: **FAB-NORTH-01**</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📡 SENSOR CONFIGURATION")
    
    # Intelligence Sources
    sources = []
    if sample_video:
        sources.append("Sample Video")
    sources.extend(["Video File", "Webcam (0)"])
    
    video_source = st.selectbox("Intelligence Source", sources)
    
    confidence_slider = st.slider("Neural Confidence Threshold", 0.1, 1.0, 0.45, step=0.01)
    line_thickness = st.slider("Annotation Line Width", 1, 5, 2)
    
    alert_classes = st.multiselect(
        "Violations To Monitor",
        options=VIOLATION_CLASSES,
        default=VIOLATION_CLASSES
    )
    
    uploaded_file = None
    if video_source == "Video File":
        uploaded_file = st.file_uploader("Upload Sector Feed", type=["mp4", "avi", "mov"])
    
    use_dshow = st.checkbox("Enhanced Hardware Access", value=True)
    
    st.markdown("---")
    st.markdown("### 🚦 SYSTEM CONTROLS")
    
    if "running" not in st.session_state: 
        st.session_state.running = False
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        start_btn = st.button("▶ START SCAN")
    with col_c2:
        stop_btn = st.button("⏹ STOP SCAN")
        
    if start_btn:
        st.session_state.running = True
        st.session_state.session_rows = []
    if stop_btn:
        st.session_state.running = False

    navigation_tip()

# ===================== MAIN HEADER =====================
mission_control_header("AEGIS <span style='color:#58a6ff;'>MISSION CONTROL</span>", 
                      "OPERATIONAL SAFETY INTELLIGENCE & REAL-TIME COMPLIANCE AUDITING")

# ===================== KPI BANNER =====================
col_k1, col_k2, col_k3, col_k4 = st.columns(4)

# Placeholders for KPIs
with col_k1: kpi_frames = st.empty()
with col_k2: kpi_violations = st.empty()
with col_k3: kpi_active = st.empty()
with col_k4: kpi_fps = st.empty()

# Helper to load initial default stats
def draw_empty_kpis():
    with col_k1: kpi_card("Scanned Frames", "0", "👁️", "#58a6ff")
    with col_k2: kpi_card("Total Breaches", "0", "🚨", "#f85149")
    with col_k3: kpi_card("Current Threat Level", "SECURE", "🛡️", "#56d364", alert_type="success")
    with col_k4: kpi_card("Sensor Latency", "STANDBY", "⚡", "#00d4ff")

draw_empty_kpis()

st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

# ===================== MONITORING GRID =====================
col_left, col_right = st.columns([2.5, 1.2])

with col_left:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#58a6ff;">💠 Live Optic Array</h3>', unsafe_allow_html=True)
    video_ph = st.empty()

with col_right:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#58a6ff;">🚨 Incident Stream</h3>', unsafe_allow_html=True)
    # Scrollable container for incident stream
    feed_ph = st.container()

# ===================== CHICKLET FEED & LOGS =====================
st.markdown("---")
c_metrics, c_logs = st.columns([1.5, 2.2])

with c_metrics:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#58a6ff;">📈 Stream Performance Timeline</h3>', unsafe_allow_html=True)
    metrics_chart_ph = st.empty()

with c_logs:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#58a6ff;">📋 Real-time Audit Log</h3>', unsafe_allow_html=True)
    logs_ph = st.empty()

# Initialize dataframes & chart placeholders
def draw_empty_metrics():
    fig = go.Figure()
    fig.update_layout(
        height=180, margin=dict(l=10, r=10, t=10, b=10),
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, title="FPS")
    )
    metrics_chart_ph.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="empty_metrics_chart")
    logs_ph.info("Awaiting sensor stream activation...")


# ===================== DETECTION ENGINE =====================
if st.session_state.running:
    detector = PPEDetector(conf=confidence_slider)
    
    # Resolve Source path
    cap_src = None
    if video_source == "Webcam (0)":
        cap_src = 0
    elif video_source == "Sample Video":
        cap_src = sample_video
    elif uploaded_file:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]).name
        with open(tmp_file, "wb") as f:
            f.write(uploaded_file.read())
        cap_src = tmp_file
    else:
        st.warning("⚠️ PROMPT REQUIRED: Please define a valid intelligence source.")
        st.session_state.running = False
        st.rerun()

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
    if "session_rows" not in st.session_state: 
        st.session_state.session_rows = []
    
    prev_time = time.time()
    total_frames = 0
    total_violations = 0
    fps_history = deque(maxlen=60)
    time_history = deque(maxlen=60)
    
    workers_list = ["WKR_101", "WKR_102", "WKR_103", "WKR_104", "WKR_105", "WKR_106", "WKR_107", "WKR_108"]

    try:
        while cap.isOpened() and st.session_state.running:
            ret, frame = cap.read()
            if not ret: 
                break

            total_frames += 1
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect (passing our custom line width)
            annotated, detections = detector.detect(rgb, line_width=line_thickness)
            
            # Filter detections based on selected alert classes
            frame_violations = 0
            rows_to_save = []
            
            for d in detections:
                class_name = d["class_name"]
                if class_name in alert_classes:
                    frame_violations += 1
                    ts_raw = datetime.now()
                    ts = ts_raw.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Save Snap relative to project root snapshots directory
                    snap_id = f"snap_{ts_raw.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                    snap_path = os.path.join("snapshots", snap_id)
                    abs_snap_path = os.path.join(SNAP_DIR, snap_id)
                    cv2.imwrite(abs_snap_path, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
                    
                    # Generate a random worker ID for visualization consistency
                    worker_id = random.choice(workers_list)
                    
                    row = [ts, worker_id, class_name, d["confidence"], 
                           int(d["bbox"]["x1"]), int(d["bbox"]["y1"]), int(d["bbox"]["x2"]), int(d["bbox"]["y2"]), 
                           snap_path, "Violation"]
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

            # Update KPI banner widgets dynamically
            with col_k1: kpi_card("Scanned Frames", total_frames, "👁️", "#58a6ff")
            with col_k2: kpi_card("Total Breaches", total_violations, "🚨", "#f85149")
            
            if frame_violations > 0:
                with col_k3: kpi_card("Current Threat Level", f"{frame_violations} BREACHES", "🔥", "#f85149", alert_type="danger")
            else:
                with col_k3: kpi_card("Current Threat Level", "SECURE", "🛡️", "#56d364", alert_type="success")
                
            with col_k4: kpi_card("Sensor Latency", f"{fps:.1f} FPS", "⚡", "#00d4ff")

            # Draw the video frame to Streamlit
            video_ph.image(annotated, use_container_width=True)
            
            # Periodic UI updates to reduce streamlit render overhead (every 3 frames)
            if total_frames % 3 == 0:
                # Plotly Chart Update
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(time_history), y=list(fps_history),
                    mode='lines', name='FPS', 
                    line=dict(color='#58a6ff', width=2),
                    fill='tozeroy', fillcolor='rgba(88, 166, 255, 0.08)'
                ))
                fig.update_layout(
                    height=180, margin=dict(l=10, r=10, t=10, b=10),
                    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, visible=False), 
                    yaxis=dict(showgrid=False, title="FPS", titlefont=dict(color="#58a6ff"), tickfont=dict(color="#58a6ff"))
                )
                metrics_chart_ph.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"fps_chart_{total_frames}")

                # Feed Update (Incident list)
                with feed_ph:
                    if st.session_state.session_rows:
                        # Clear old list and draw recent 4
                        recent_logs = st.session_state.session_rows[-4:]
                        for r_log in reversed(recent_logs):
                            draw_incident_card(
                                timestamp=r_log[0].split(" ")[1], 
                                breach_type=r_log[2], 
                                worker_id=r_log[1], 
                                confidence=r_log[3], 
                                snap_path=r_log[8],
                                status=r_log[9]
                            )
                    else:
                        st.info("No safety breaches recorded in this session.")

                # Table Logs Update
                if st.session_state.session_rows:
                    logs_df = pd.DataFrame(st.session_state.session_rows, columns=CSV_HEADER).tail(30)
                    logs_ph.dataframe(logs_df[["timestamp", "worker_id", "violation_type", "confidence", "status"]], use_container_width=True)

            time.sleep(0.005)

    finally:
        cap.release()
        st.session_state.running = False
        st.success("✅ MISSION COMPLETED: Sensor stream successfully terminated.")

else:
    # Standby Mode UI presentation
    draw_empty_kpis()
    
    # Standby video placeholder: show a cool glowing interface or graphic
    video_ph.markdown("""
    <div style="background-color:#0b0f19; border: 1px dashed rgba(88,166,255,0.2); border-radius:16px; padding: 80px 20px; text-align:center; box-shadow: inset 0 0 30px rgba(0,0,0,0.5);">
        <div style="font-size:4rem; margin-bottom: 20px; filter: drop-shadow(0 0 10px rgba(88,166,255,0.3));">📡</div>
        <h3 style="color:#58a6ff; font-weight:700; margin-bottom: 10px;">STANDBY MODE</h3>
        <p style="color:rgba(255,255,255,0.45); font-size:0.9rem; max-width:400px; margin: 0 auto;">
            Awaiting active sensor link. Please configure your Neural parameters in the left sidebar and click <b>START SCAN</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Draw empty metrics logs
    draw_empty_metrics()
