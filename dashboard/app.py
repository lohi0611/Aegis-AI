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

# Ensure LOG_CSV resolves to project root violations.csv
def resolve_log_csv():
    candidates = [
        os.path.join(project_root, "violations.csv"),
        os.path.join(current_dir, "violations.csv"),
        "violations.csv"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return os.path.join(project_root, "violations.csv")

LOG_CSV = resolve_log_csv()
SNAP_DIR = os.path.join(project_root, "snapshots")
os.makedirs(SNAP_DIR, exist_ok=True)

# Find Sample Video
sample_video_paths = [
    os.path.join(current_dir, "uploaded_video.mp4"),
    os.path.join(project_root, "uploaded_video.mp4"),
    os.path.join(project_root, "assets", "finalTest.mp4"),
    os.path.join(project_root, "infosys", "dataset", "source_files", "source_files", "hardhat.mp4"),
    os.path.join(project_root, "infosys", "dataset", "source_files", "source_files", "JapanPPE.mp4"),
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
    st.markdown('<div style="text-align: center; margin-bottom: 15px;"><span style="font-size: 2.2rem;">🛡️</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.25rem; font-weight: 800; color: #ffffff; text-align: center; letter-spacing: 1px; margin-bottom: 4px;">AegisAI Safety</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.75rem; color: #9ca3af; text-align: center; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 20px;">Workplace Monitoring Station</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ⚙️ CONFIGURATION")
    
    # Input Sources
    sources = ["Laptop Camera (Browser)"]
    if sample_video:
        sources.append("Sample Video")
    sources.extend(["Upload Video File", "Local Webcam (OpenCV)"])
    
    video_source = st.selectbox("Video Input Source", sources)
    
    confidence_slider = st.slider("Detection Confidence Threshold", 0.1, 1.0, 0.25, step=0.01)
    line_thickness = st.slider("Bounding Box Thickness", 1, 5, 2)
    
    alert_classes = st.multiselect(
        "Violations To Monitor",
        options=VIOLATION_CLASSES,
        default=VIOLATION_CLASSES
    )
    
    uploaded_file = None
    if video_source == "Video File":
        uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "avi", "mov"])
    
    use_dshow = st.checkbox("Enhanced Hardware Access", value=True)
    
    st.markdown("---")
    st.markdown("### 🎮 CONTROL PANEL")
    
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
mission_control_header("AEGIS AI <span style='color:#3b82f6;'>SAFETY CONTROL</span>", 
                      "REAL-TIME PPE COMPLIANCE SURVEILLANCE & INCIDENT MONITORING")

# ===================== KPI BANNER =====================
col_k1, col_k2, col_k3, col_k4 = st.columns(4)

# Placeholders for KPIs
with col_k1: kpi_frames = st.empty()
with col_k2: kpi_violations = st.empty()
with col_k3: kpi_active = st.empty()
with col_k4: kpi_fps = st.empty()

# Helper to load initial default stats
def draw_empty_kpis():
    with col_k1: kpi_card("Scanned Frames", "0", "👁️", "#3b82f6")
    with col_k2: kpi_card("Total Breaches", "0", "🚨", "#ef4444")
    with col_k3: kpi_card("Current Threat Level", "SECURE", "🛡️", "#10b981", alert_type="success")
    with col_k4: kpi_card("Sensor Latency", "STANDBY", "⚡", "#06b6d4")

st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

# ===================== MONITORING GRID =====================
col_left, col_right = st.columns([2.5, 1.2])

with col_left:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#3b82f6;">📹 Live Feed Stream</h3>', unsafe_allow_html=True)
    video_ph = st.empty()

with col_right:
    st.markdown('<h3 style="margin-bottom:15px; font-weight:600; color:#3b82f6;">📋 Recent Alerts</h3>', unsafe_allow_html=True)
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
if video_source == "Laptop Camera (Browser)":
    detector = PPEDetector(conf=confidence_slider)
    with video_ph.container():
        st.markdown('<p style="color:#60a5fa; font-weight:600; margin-bottom:8px;">📷 Live Browser Camera Input</p>', unsafe_allow_html=True)
        img_file = st.camera_input("Snapshot from Laptop Camera", key="laptop_camera_widget")
    
    if img_file:
        bytes_data = img_file.getvalue()
        frame = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        annotated, detections = detector.detect(frame, line_width=line_thickness, alert_classes=alert_classes)
        
        # Display annotated result
        video_ph.image(annotated, channels="BGR", use_container_width=True)
        
        # Update KPIs
        frame_violations = len(detections)
        with col_k1: kpi_card("Scanned Frames", "1", "👁️", "#3b82f6")
        with col_k2: kpi_card("Total Breaches", str(frame_violations), "🚨", "#ef4444")
        if frame_violations > 0:
            with col_k3: kpi_card("Current Threat Level", f"{frame_violations} BREACHES", "🔥", "#ef4444", alert_type="danger")
        else:
            with col_k3: kpi_card("Current Threat Level", "SECURE", "🛡️", "#10b981", alert_type="success")
        with col_k4: kpi_card("Sensor Latency", "LIVE", "⚡", "#06b6d4")
        
        # Log breaches to session, incident stream, and CSV if any detected
        if frame_violations > 0:
            workers_list = ["WKR_101", "WKR_102", "WKR_103", "WKR_104"]
            with feed_ph:
                for det in detections:
                    box = det["bbox"]
                    cls_name = det["class_name"]
                    conf_val = det["confidence"]
                    w_id = random.choice(workers_list)
                    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Save snapshot
                    snap_filename = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                    snap_full_path = os.path.join(SNAP_DIR, snap_filename)
                    cv2.imwrite(snap_full_path, annotated)
                    
                    snap_rel_path = f"snapshots/{snap_filename}"
                    row = [timestamp_str, w_id, cls_name, round(conf_val, 2), box[0], box[1], box[2], box[3], snap_rel_path, "Violation"]
                    
                    if "session_rows" not in st.session_state:
                        st.session_state.session_rows = []
                    st.session_state.session_rows.append(row)
                    
                    # Draw Incident Card in Incident Stream feed
                    draw_incident_card(
                        timestamp=timestamp_str.split(" ")[1],
                        breach_type=cls_name,
                        worker_id=w_id,
                        confidence=conf_val,
                        snap_path=snap_rel_path,
                        status="Violation"
                    )
                    
                    # Append to CSV
                    with open(LOG_CSV, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(row)

elif st.session_state.running:
    detector = PPEDetector(conf=confidence_slider)
    
    # Resolve Source path smoothly
    cap_src = None
    if video_source == "Sample Video" and sample_video:
        cap_src = sample_video
    elif uploaded_file:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]).name
        with open(tmp_file, "wb") as f:
            f.write(uploaded_file.read())
        cap_src = tmp_file
    elif video_source == "Local Webcam (OpenCV)":
        cap_src = 0
    
    # Fallback if source is missing
    if cap_src is None:
        if sample_video:
            cap_src = sample_video
            st.info("ℹ️ Using sample video stream for demonstration.")
        else:
            st.warning("⚠️ Please upload a video file or select a valid video source.")
            st.session_state.running = False
            st.stop()

    # Open Video Capture
    cap = None
    if isinstance(cap_src, int) and cap_src == 0 and use_dshow:
        cap = cv2.VideoCapture(cap_src, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(cap_src)
    
    # Fallback if capture fails (e.g. webcam not found on cloud server)
    if not cap or not cap.isOpened():
        if cap_src != sample_video and sample_video:
            st.info("ℹ️ Local OpenCV webcam not accessible on cloud server. Select 'Laptop Camera (Browser)' in sidebar or use sample video.")
            cap = cv2.VideoCapture(sample_video)
        
    if not cap or not cap.isOpened():
        st.error("🚨 Unable to access video stream.")
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
            
            # Detect (passing our custom line width and alert classes)
            annotated, detections = detector.detect(rgb, line_width=line_thickness, alert_classes=alert_classes)
            
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
                           int(d["bbox"][0]), int(d["bbox"][1]), int(d["bbox"][2]), int(d["bbox"][3]), 
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
    
    # Standby video placeholder: show a clean professional interface
    video_ph.markdown("""
    <div style="background-color:#111827; border: 1px dashed #374151; border-radius:12px; padding: 70px 20px; text-align:center;">
        <div style="font-size:3.5rem; margin-bottom: 15px;">📹</div>
        <h3 style="color:#ffffff; font-weight:700; margin-bottom: 8px;">CAMERA STREAM STANDBY</h3>
        <p style="color:#9ca3af; font-size:0.875rem; max-width:420px; margin: 0 auto;">
            Camera stream is currently offline. Select an input source in the sidebar and click <b>START SCAN</b> to begin real-time safety monitoring.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Draw empty metrics logs
    draw_empty_metrics()
