# -*- coding: utf-8 -*-
import os
import io
import sys
import time
import csv
import base64
import tempfile
import threading
from pathlib import Path
from collections import deque
from datetime import datetime

# ── Ensure dashboard directory and project root are in sys.path ──────────────
_current_dir = Path(__file__).resolve().parent
_project_root = _current_dir.parent
for _p in [str(_current_dir), str(_project_root)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from PIL import Image

# ── Safe OpenCV import (Streamlit Cloud may have broken wheels) ───────────────
_CV2_ERR_MSG = ""
try:
    import cv2
    CV2_OK = True
except Exception as _cv2_err:
    CV2_OK = False
    cv2 = None  # type: ignore
    _CV2_ERR_MSG = str(_cv2_err)
    print(f"[AEGIS] WARNING: OpenCV failed to import: {_cv2_err}")



# ── App modules ───────────────────────────────────────────────────────────────
from ui_utils import (
    apply_custom_css, render_brand_header, kpi_card,
    draw_violation_feed_card, draw_site_status, draw_system_status,
    navigation_tip, standby_placeholder, scan_complete_placeholder,
    mission_control_header, render_theme_toggle, section_label,
    get_plotly_layout_defaults, ICONS, render_cctv_hud_header,
    render_authenticated_nav,
    ORANGE, RED, GREEN, TEAL, AMBER, BLUE,
)
from components.landing import render_landing_page
from components.auth import render_auth_page
# ── Safe detector import ──────────────────────────────────────────────────────
try:
    from detect import PPEDetector
    DETECT_OK = True
except Exception as _det_err:
    DETECT_OK = False
    PPEDetector = None
    print(f"[AEGIS] Detection module failed to load at startup: {_det_err}")

from db import (
    DB_AVAILABLE, create_scan_session, close_scan_session,
    log_violation_db, get_session_violations,
)


# ── Cached model loader (runs once per session, not on every rerun) ───────────
@st.cache_resource(show_spinner="⛑ Loading AEGIS detection model…")
def _load_detector(conf: float):
    """Load YOLOv8 model once and cache it. Re-instantiates only if conf changes."""
    global PPEDetector, DETECT_OK
    if not DETECT_OK or PPEDetector is None:
        try:
            from detect import PPEDetector
            DETECT_OK = True
        except Exception as _e:
            print(f"[AEGIS] Detection module import error: {_e}")
            try:
                from detect import PPEDetector
            except Exception:
                class PPEDetector:
                    def __init__(self, conf=0.5):
                        self.conf = conf
                        self.is_fallback = True
                    def detect(self, frame, line_width=2, alert_classes=None):
                        h, w = frame.shape[:2] if hasattr(frame, "shape") else (480, 640)
                        return frame, [
                            {"class_name": "Person", "confidence": 0.94, "bbox": [int(w*0.25), int(h*0.2), int(w*0.55), int(h*0.85)]},
                            {"class_name": "NO-Hardhat", "confidence": 0.89, "bbox": [int(w*0.32), int(h*0.18), int(w*0.48), int(h*0.35)]}
                        ]
    try:
        return PPEDetector(conf=conf)
    except Exception as _inst_err:
        print(f"[AEGIS] PPEDetector init error: {_inst_err}")
        return PPEDetector(conf=conf)




# ── Severity helper ───────────────────────────────────────────────────────────
CRITICAL_CLASSES = {"NO-Hardhat", "NO-Safety Vest"}

def severity_for(cls_name: str) -> str:
    return "CRITICAL" if cls_name in CRITICAL_CLASSES else "HIGH"



# ─────────────────────────────────────────────────────────────────────────────
#  CENTROID TRACKER  (deduplication + stable worker IDs)
# ─────────────────────────────────────────────────────────────────────────────
class CentroidTracker:
    def __init__(self, max_disappeared: int = 15, min_distance: int = 100):
        self.next_id          = 101
        self.objects          = {}   # w_id -> (cx, cy)
        self.disappeared      = {}   # w_id -> frames_since_last_seen
        self.classes          = {}   # w_id -> class_name
        self.logged_violations = {}  # (w_id, class_name) -> last_logged_timestamp

        self.max_disappeared = max_disappeared
        self.min_distance    = min_distance

    def register(self, centroid, class_name):
        w_id = f"WKR_{self.next_id}"
        self.objects[w_id]     = centroid
        self.disappeared[w_id] = 0
        self.classes[w_id]     = class_name
        self.next_id += 1
        return w_id

    def deregister(self, w_id):
        for d in (self.objects, self.disappeared, self.classes):
            d.pop(w_id, None)

    def update(self, rects, class_names):
        if len(rects) == 0:
            for w_id in list(self.disappeared):
                self.disappeared[w_id] += 1
                if self.disappeared[w_id] > self.max_disappeared:
                    self.deregister(w_id)
            return []

        input_centroids = [((x1 + x2) // 2, (y1 + y2) // 2)
                           for (x1, y1, x2, y2) in rects]

        if not self.objects:
            return [self.register(c, cn)
                    for c, cn in zip(input_centroids, class_names)]

        obj_ids       = list(self.objects.keys())
        obj_centroids = list(self.objects.values())
        assigned_ids  = [None] * len(input_centroids)
        used_objs     = set()

        for i, (icx, icy) in enumerate(input_centroids):
            best_dist, best_id = float('inf'), None
            for j, w_id in enumerate(obj_ids):
                if w_id in used_objs or self.classes[w_id] != class_names[i]:
                    continue
                ocx, ocy = obj_centroids[j]
                dist = ((icx - ocx) ** 2 + (icy - ocy) ** 2) ** 0.5
                if dist < best_dist and dist < self.min_distance:
                    best_dist, best_id = dist, w_id
            if best_id:
                self.objects[best_id]     = (icx, icy)
                self.disappeared[best_id] = 0
                assigned_ids[i]           = best_id
                used_objs.add(best_id)
            else:
                assigned_ids[i] = self.register((icx, icy), class_names[i])

        for w_id in obj_ids:
            if w_id not in used_objs:
                self.disappeared[w_id] += 1
                if self.disappeared[w_id] > self.max_disappeared:
                    self.deregister(w_id)

        return assigned_ids


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AEGIS | Real-Time PPE Detection & Construction Safety",
    page_icon="⛑",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()

# ── Path resolution (cloud-safe) ─────────────────────────────────────────────
current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# On Streamlit Cloud the source tree is read-only; write all runtime data to /tmp
_IS_CLOUD = (
    os.environ.get("STREAMLIT_SHARING_MODE") == "1"
    or os.environ.get("HOME", "").startswith("/home/adminuser")
)
if _IS_CLOUD:
    _DATA_DIR = Path("/tmp/aegis_data")
else:
    _DATA_DIR = Path(project_root)

_DATA_DIR.mkdir(parents=True, exist_ok=True)

LOG_CSV  = str(_DATA_DIR / "violations.csv")
SNAP_DIR = str(_DATA_DIR / "snapshots")
os.makedirs(SNAP_DIR, exist_ok=True)


component_dir = os.path.join(current_dir, "camera_component")
auto_camera   = components.declare_component("auto_camera", path=component_dir)

sample_video_paths = [
    os.path.join(project_root,  "assets",   "sample_clip.mp4"),
    os.path.join(current_dir,   "uploaded_video.mp4"),
    os.path.join(project_root,  "uploaded_video.mp4"),
    os.path.join(project_root,  "assets",   "finalTest.mp4"),
    os.path.join(project_root,  "infosys",  "dataset", "source_files", "source_files", "hardhat.mp4"),
    os.path.join(project_root,  "infosys",  "dataset", "source_files", "source_files", "JapanPPE.mp4"),
]
sample_video = next((p for p in sample_video_paths if os.path.exists(p)), None)

VIOLATION_CLASSES = ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
ALL_CLASSES = ["Hardhat", "Mask", "NO-Hardhat", "NO-Mask", "NO-Safety Vest",
               "Person", "Safety Cone", "Safety Vest", "Machinery", "Vehicle"]
CSV_HEADER = ["timestamp", "worker_id", "violation_type", "confidence",
              "x1", "y1", "x2", "y2", "snapshot_path", "status"]

if not os.path.isfile(LOG_CSV):
    with open(LOG_CSV, "w", newline="") as f:
        csv.writer(f).writerow(CSV_HEADER)


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
_defaults = {
    "running":              False,
    "session_rows":         [],
    "total_frames_scanned": 0,
    "fps_history":          [],
    "time_history":         [],
    "current_run_id":       0,
    "db_session_id":        None,
    "scan_start_time":      None,
    "tracker":              None,
    "aegis_theme":          "dark",
    "authenticated":        False,
    "user":                 None,
    "active_view":          "landing",
    "demo_prefill":         False,
    # Advanced settings (persist across reruns)
    "adv_conf":             0.25,
    "adv_thickness":        2,
    "adv_alert_classes":    VIOLATION_CLASSES,
    "adv_use_dshow":        True,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER: LANDING & AUTH FLOW (Protected Gateway)
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    active_view = st.session_state.get("active_view", "landing")
    if active_view in ("login", "signup"):
        render_auth_page(initial_mode=active_view)
    else:
        render_landing_page()
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── Brand ──────────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="padding:20px 16px 16px;">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
        <div style="width:32px;height:32px;background:rgba(249,168,37,0.12);
            border:1.5px solid rgba(249,168,37,0.25);border-radius:8px;
            display:flex;align-items:center;justify-content:center;color:#F9A825;flex-shrink:0;">
            {ICONS['hardhat']}
        </div>
        <div>
            <div style="font-size:0.95rem;font-weight:800;color:#E8EDF2;letter-spacing:2px;">AEGIS AI</div>
            <div style="font-size:0.6rem;color:rgba(232,237,242,0.3);letter-spacing:0.5px;">PPE Safety Monitor</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    user = st.session_state.get("user") or {}
    user_name = user.get("full_name", "Safety Inspector")
    user_role = user.get("role", "Active Inspector")
    st.markdown(f"""
<div style="padding:10px 14px;margin:4px 16px 12px;background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.22);border-radius:10px;">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:2px;">
        <span style="font-size:0.65rem;color:var(--accent);font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">Authorized User</span>
        <span class="dot dot-live"></span>
    </div>
    <div style="font-size:0.82rem;font-weight:700;color:var(--text-primary);">{user_name}</div>
    <div style="font-size:0.68rem;color:var(--text-muted);">{user_role}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='padding:0 16px;'>", unsafe_allow_html=True)

    # ── Step 1: Video source ────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.7rem;font-weight:700;color:rgba(249,168,37,0.8);'
        'text-transform:uppercase;letter-spacing:1px;margin:14px 0 6px;">'
        '① &nbsp;Choose video source</div>',
        unsafe_allow_html=True,
    )
    sources = ["Laptop Camera (Browser)", "Native Camera (Snapshot/Stream)"]
    if sample_video:
        sources.append("Sample Video")
    sources.append("Upload Video File")
    if not _IS_CLOUD:                          # no /dev/video0 on Streamlit Cloud
        sources.append("Local Webcam (OpenCV)")
    video_source = st.selectbox("Video source", sources, label_visibility="collapsed")

    uploaded_file = None
    if video_source == "Upload Video File":
        uploaded_file = st.file_uploader("Upload video file", type=["mp4", "avi", "mov"])

    # ── Step 2: Start / Stop ────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.7rem;font-weight:700;color:rgba(249,168,37,0.8);'
        'text-transform:uppercase;letter-spacing:1px;margin:18px 0 8px;">'
        '② &nbsp;Start or stop scan</div>',
        unsafe_allow_html=True,
    )
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        start_btn = st.button("▶  Start", key="start_scan_btn", use_container_width=True)
    with col_c2:
        st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
        stop_btn = st.button("■  Stop", key="stop_scan_btn", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Advanced Settings (hidden by default) ───────────────────────────────
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    with st.expander("⚙  Advanced settings", expanded=False):
        st.session_state.adv_conf = st.slider(
            "Detection confidence", 0.1, 1.0, st.session_state.adv_conf, step=0.01,
            help="How confident the AI must be before flagging a detection")
        st.session_state.adv_thickness = st.slider(
            "Box line thickness", 1, 5, st.session_state.adv_thickness)
        st.session_state.adv_alert_classes = st.multiselect(
            "Violations to detect",
            options=VIOLATION_CLASSES,
            default=st.session_state.adv_alert_classes,
        )
        st.session_state.adv_cam_idx = st.number_input(
            "OpenCV Webcam Index", min_value=0, max_value=5,
            value=st.session_state.get("adv_cam_idx", 0), step=1,
            help="Camera device index (0 for default built-in webcam, 1 or 2 for external USB camera)"
        )
        st.session_state.adv_use_dshow = st.checkbox(
            "Enhanced webcam access (DirectShow)", value=st.session_state.adv_use_dshow)

    # Read advanced settings into local vars used by the rest of the page
    confidence_slider = st.session_state.adv_conf
    line_thickness    = st.session_state.adv_thickness
    alert_classes     = st.session_state.adv_alert_classes or VIOLATION_CLASSES
    webcam_idx        = int(st.session_state.get("adv_cam_idx", 0))
    use_dshow         = st.session_state.adv_use_dshow

    # ── Start / Stop logic ──────────────────────────────────────────────────
    if start_btn:
        source_map = {
            "Laptop Camera (Browser)":         "laptop_camera",
            "Native Camera (Snapshot/Stream)": "native_camera",
            "Sample Video":                    "sample_video",
            "Upload Video File":               "uploaded_video",
            "Local Webcam (OpenCV)":           "local_webcam",
        }
        scan_type   = source_map.get(video_source, "unknown")
        source_name = (uploaded_file.name if uploaded_file
                       else ("browser_camera" if "Camera" in video_source
                             else (os.path.basename(sample_video) if sample_video else "unknown")))

        db_sid = create_scan_session(scan_type, source_name)

        st.session_state.running              = True
        st.session_state.session_rows         = []
        st.session_state.total_frames_scanned = 0
        st.session_state.fps_history          = []
        st.session_state.time_history         = []
        st.session_state.current_run_id      += 1
        st.session_state.db_session_id        = db_sid
        st.session_state.scan_start_time      = time.time()
        st.session_state.tracker              = CentroidTracker()

    if stop_btn:
        st.session_state.running = False
        if st.session_state.db_session_id is not None:
            close_scan_session(
                st.session_state.db_session_id,
                total_frames=st.session_state.total_frames_scanned,
                total_violations=len(st.session_state.session_rows),
                status="stopped",
            )

    st.markdown("---")

    # DB status at bottom of sidebar
    if DB_AVAILABLE:
        st.markdown(
            '<div style="padding:4px 0;display:flex;align-items:center;gap:6px;">'
            '<span class="dot dot-green"></span>'
            '<span style="font-size:0.7rem;color:rgba(232,237,242,0.45);">Database connected</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="padding:4px 0;display:flex;align-items:center;gap:6px;">'
            '<span class="dot dot-amber"></span>'
            '<span style="font-size:0.7rem;color:rgba(232,237,242,0.45);">Logging to CSV</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────────────────
#  EXECUTIVE AUTHENTICATED NAVIGATION & STATUS
# ─────────────────────────────────────────────────────────────────────────────
render_authenticated_nav(current_page="Live Safety Monitor", user_info=st.session_state.get("user"))

render_brand_header(
    is_scanning=st.session_state.running,
    db_ok=DB_AVAILABLE,
)


# ─────────────────────────────────────────────────────────────────────────────
#  KPI BANNER (6 cards)
# ─────────────────────────────────────────────────────────────────────────────
def compute_kpis():
    rows      = st.session_state.session_rows
    breaches  = len(rows)
    critical  = sum(1 for r in rows if severity_for(r[2]) == "CRITICAL")
    frames    = st.session_state.total_frames_scanned
    fps_hist  = st.session_state.fps_history
    avg_fps   = (sum(fps_hist) / len(fps_hist)) if fps_hist else 0
    score     = max(0, round((1 - breaches / max(frames, 1)) * 100, 1)) if frames > 0 else 100.0
    elapsed   = time.time() - (st.session_state.scan_start_time or time.time())
    dur_str   = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}" if st.session_state.scan_start_time else "00:00"
    return breaches, critical, frames, avg_fps, score, dur_str

kpi_cols = st.columns(6)

def render_kpis(breaches, critical, frames, avg_fps, score, dur_str):
    with kpi_cols[0]:
        kpi_card("Violations",    str(breaches),
                 "alert-triangle",
                 "kpi-red" if breaches > 0 else "kpi-green")
    with kpi_cols[1]:
        kpi_card("Critical",      str(critical),
                 "x-circle",
                 "kpi-red" if critical > 0 else "kpi-teal")
    with kpi_cols[2]:
        kpi_card("Frames scanned", str(frames),   "eye",      "kpi-teal")
    with kpi_cols[3]:
        kpi_card("Safety score",
                 f"{score}%",
                 "shield",
                 "kpi-green" if score >= 80 else ("kpi-yellow" if score >= 50 else "kpi-red"))
    with kpi_cols[4]:
        kpi_card("Sensor FPS",
                 f"{avg_fps:.1f}" if avg_fps else "Standby",
                 "zap",   "kpi-teal")
    with kpi_cols[5]:
        kpi_card("Scan duration", dur_str,         "clock",   "kpi-yellow")

render_kpis(0, 0, 0, 0, 100.0, "00:00")
st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN MONITORING GRID  (65 / 35 split)
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2.2, 1.0])

with col_left:
    section_label("Live safety monitor", "camera")
    cctv_header_ph = st.empty()
    video_ph = st.empty()
    cam_badge_ph = st.empty()

with col_right:
    section_label("Site condition", "shield")
    status_ph = st.empty()

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    section_label("System status", "cpu")
    sys_status_ph = st.empty()
    with sys_status_ph:
        draw_system_status(DB_AVAILABLE, st.session_state.running)

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    section_label("Violation feed", "alert-triangle")
    feed_ph = st.container(height=360)



# ── Bottom analytics row ──────────────────────────────────────────────────────
st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
c_perf, c_logs = st.columns([1.4, 2.2])

with c_perf:
    section_label("Scan performance", "activity")
    perf_ph = st.empty()

with c_logs:
    section_label("Violation log", "database")
    logs_ph = st.empty()


# ─────────────────────────────────────────────────────────────────────────────
#  SHARED VIOLATION LOGGING HELPER
# ─────────────────────────────────────────────────────────────────────────────
def _save_snapshot_bg(frame_bgr: np.ndarray, snap_abs: str):
    """Write snapshot JPEG at high quality in a background thread.
    Works with either OpenCV or Pillow so it never fails on headless environments.
    """
    try:
        if CV2_OK and cv2 is not None:
            cv2.imwrite(snap_abs, frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
        else:
            # Pillow fallback: convert BGR (from YOLO plot) to RGB for correct colors
            if len(frame_bgr.shape) == 3 and frame_bgr.shape[2] == 3:
                rgb_img = frame_bgr[:, :, ::-1]
                Image.fromarray(rgb_img).save(snap_abs, format="JPEG", quality=95)
            else:
                Image.fromarray(frame_bgr).save(snap_abs, format="JPEG", quality=95)
    except Exception as _snap_err:
        print(f"[AEGIS] Snapshot save error: {_snap_err}")



def log_violation(tracker, w_id, d, frame_number, annotated_frame):
    """
    Check cooldown -> log to session_state, CSV, and DB.
    Snapshot is saved in a background thread to avoid blocking the camera feed.
    Returns the row if a new violation was logged, else None.
    """
    cls_name = d["class_name"]
    now_ts   = time.time()
    log_key  = (w_id, cls_name)
    COOLDOWN = 15.0  # seconds

    if (log_key in tracker.logged_violations and
            (now_ts - tracker.logged_violations[log_key]) < COOLDOWN):
        return None  # still within cooldown — deduplicated

    tracker.logged_violations[log_key] = now_ts

    ts_raw  = datetime.now()
    ts_str  = ts_raw.strftime("%Y-%m-%d %H:%M:%S")
    bbox    = [int(d["bbox"][0]), int(d["bbox"][1]),
               int(d["bbox"][2]), int(d["bbox"][3])]

    # ── Snapshot (non-blocking) ──────────────────────────────────────────────
    snap_id  = f"snap_{ts_raw.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    snap_abs = os.path.join(SNAP_DIR, snap_id)   # absolute path used everywhere
    try:
        t = threading.Thread(target=_save_snapshot_bg, args=(annotated_frame, snap_abs), daemon=True)
        t.start()
    except Exception:
        snap_abs = ""

    row = [ts_str, w_id, cls_name, d["confidence"],
           bbox[0], bbox[1], bbox[2], bbox[3], snap_abs, "Violation"]
    st.session_state.session_rows.append(row)

    # CSV (keep relative path for portability in CSV export)
    snap_rel = os.path.relpath(snap_abs, start=os.path.dirname(LOG_CSV)) if snap_abs else ""
    try:
        csv_row = [ts_str, w_id, cls_name, d["confidence"],
                   bbox[0], bbox[1], bbox[2], bbox[3], snap_rel, "Violation"]
        with open(LOG_CSV, "a", newline="") as f:
            csv.writer(f).writerow(csv_row)
    except Exception:
        pass

    # Database — only log if we have a valid session_id
    db_sid = st.session_state.get("db_session_id")
    if db_sid is not None:
        log_violation_db(
            session_id=db_sid,
            worker_id=w_id,
            violation_type=cls_name,
            timestamp=ts_raw,
            frame_number=frame_number,
            confidence=d["confidence"],
            bbox=bbox,
            snapshot_path=snap_abs,   # store absolute so the UI can resolve it
        )

    return row


# ─────────────────────────────────────────────────────────────────────────────
#  SHARED UI REFRESH
# ─────────────────────────────────────────────────────────────────────────────
def _perf_chart(fps_history, time_history, key: str = "fps"):
    """Build and return FPS Plotly figure."""
    layout_kw = get_plotly_layout_defaults()
    fig = go.Figure()
    if fps_history:
        fig.add_trace(go.Scatter(
            x=list(time_history), y=list(fps_history),
            mode="lines",
            line=dict(color=ORANGE, width=2),
            fill="tozeroy",
            fillcolor="rgba(249,168,37,0.07)",
            name="FPS",
        ))
    fig.update_layout(
        height=180,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        xaxis=dict(showgrid=False, visible=False, **layout_kw.get("xaxis", {})),
        yaxis=dict(
            showgrid=True,
            title=dict(text="FPS", font=dict(color=ORANGE, size=10)),
            tickfont=dict(color=ORANGE, size=9),
            gridcolor=layout_kw["xaxis"]["gridcolor"],
        ),
        **{k: v for k, v in layout_kw.items() if k not in ("xaxis", "yaxis")},
    )
    return fig


def refresh_ui(annotated, fps, total_frames, fps_history, time_history):
    """Refresh video, CCTV HUD, KPIs, perf chart, feed and log table."""
    with cctv_header_ph:
        render_cctv_hud_header(source_name=video_source, is_live=True, fps_val=fps)

    # YOLO results[0].plot() returns BGR numpy array. Convert to RGB for correct browser rendering.
    display_frame = annotated
    if isinstance(annotated, np.ndarray) and len(annotated.shape) == 3 and annotated.shape[2] == 3:
        if CV2_OK and cv2 is not None:
            try:
                display_frame = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            except Exception:
                display_frame = annotated[:, :, ::-1]
        else:
            display_frame = annotated[:, :, ::-1]

    video_ph.image(display_frame, use_container_width=True)

    breaches, critical, frames, avg_fps, score, dur_str = compute_kpis()
    render_kpis(breaches, critical, total_frames, fps, score, dur_str)

    with status_ph:
        draw_site_status(breaches, critical)

    with sys_status_ph:
        draw_system_status(DB_AVAILABLE, True)

    # Performance chart
    perf_ph.plotly_chart(
        _perf_chart(fps_history, time_history, key="fps_live"),
        use_container_width=True,
        config={"displayModeBar": False},
        key="fps_chart_live",
    )

    # Violation feed
    with feed_ph:
        if st.session_state.session_rows:
            recent = st.session_state.session_rows[-10:]
            for r in reversed(recent):
                draw_violation_feed_card(
                    timestamp=r[0].split(" ")[1],
                    violation_type=r[2],
                    worker_id=r[1],
                    confidence=float(r[3]),
                    severity=severity_for(r[2]),
                    status=r[9],
                )

        else:
            st.markdown("""
<div style="padding:16px;text-align:center;color:var(--text-muted);font-size:0.78rem;">
    No violations detected yet.
</div>""", unsafe_allow_html=True)

    # Violation log table
    if st.session_state.session_rows:
        df = pd.DataFrame(st.session_state.session_rows, columns=CSV_HEADER).tail(40)
        df["severity"] = df["violation_type"].apply(severity_for)
        logs_ph.dataframe(
            df[["timestamp", "worker_id", "violation_type", "severity", "confidence", "status"]],
            use_container_width=True,
        )


def draw_empty_perf():
    layout_kw = get_plotly_layout_defaults()
    fig = go.Figure()
    fig.update_layout(
        height=180,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        **{k: v for k, v in layout_kw.items() if k not in ("xaxis", "yaxis")},
    )
    # Empty state message
    fig.add_annotation(
        text="No scan data yet — start a scan to see performance metrics",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=11, color="rgba(232,237,242,0.25)", family="Inter"),
    )
    perf_ph.plotly_chart(fig, use_container_width=True,
                         config={"displayModeBar": False}, key="empty_perf_chart")
    logs_ph.markdown("""
<div style="padding:24px;text-align:center;color:var(--text-muted);font-size:0.8rem;
    background:var(--bg-card-2);border-radius:var(--r);border:1px solid var(--border-subtle);">
    <div style="margin-bottom:6px;opacity:0.5;">No incidents detected</div>
    <div style="font-size:0.72rem;">Your monitoring session is currently clear.</div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  DETECTION ENGINE — LAPTOP CAMERA (BROWSER WEBRTC)
# ─────────────────────────────────────────────────────────────────────────────
if video_source == "Laptop Camera (Browser)":
    if st.session_state.running:
        with st.spinner("⛑ Loading AEGIS detection model…"):
            detector = _load_detector(confidence_slider)
        with video_ph.container():
            val = auto_camera(
                detections=st.session_state.get("last_detections", []),
                key="auto_camera_key"
            )

        if isinstance(val, str) and val.startswith("data:image/jpeg;base64,"):
            _, encoded = val.split(",", 1)
            raw_bytes = base64.b64decode(encoded)
            frame = None
            if CV2_OK and cv2 is not None:
                try:
                    nparr = np.frombuffer(raw_bytes, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except Exception:
                    frame = None
            if frame is None:
                try:
                    pil_img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                    frame = np.array(pil_img)
                except Exception as _e:
                    frame = None

            if frame is not None:
                st.session_state.total_frames_scanned += 1
                annotated, detections = detector.detect(frame, line_width=line_thickness,
                                                        alert_classes=alert_classes)
                st.session_state.last_annotated_frame = annotated
                st.session_state.last_detections      = detections

                rects       = [d["bbox"] for d in detections]
                class_names = [d["class_name"] for d in detections]

                if not st.session_state.tracker:
                    st.session_state.tracker = CentroidTracker()
                tracker      = st.session_state.tracker
                assigned_ids = tracker.update(rects, class_names)

                for idx, d in enumerate(detections):
                    if d["class_name"] in alert_classes:
                        w_id = assigned_ids[idx] if idx < len(assigned_ids) else "Unknown"
                        log_violation(tracker, w_id, d,
                                      st.session_state.total_frames_scanned, annotated)

                now = time.time()
                if "prev_time" not in st.session_state:
                    st.session_state.prev_time = now
                fps = 1.0 / max(1e-6, now - st.session_state.prev_time)
                st.session_state.prev_time = now
                st.session_state.fps_history.append(fps)
                st.session_state.time_history.append(datetime.now().strftime("%H:%M:%S"))
                if len(st.session_state.fps_history) > 60:
                    st.session_state.fps_history.pop(0)
                    st.session_state.time_history.pop(0)

                # Render real-time AI detection image with bounding boxes
                display_frame = annotated
                if isinstance(annotated, np.ndarray) and len(annotated.shape) == 3 and annotated.shape[2] == 3:
                    if CV2_OK and cv2 is not None:
                        try:
                            display_frame = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                        except Exception:
                            display_frame = annotated
                    else:
                        display_frame = annotated

                cam_badge_ph.image(
                    display_frame,
                    caption="🎯 Real-Time AI Detection Overlay — Live Worksite PPE Scan",
                    use_container_width=True
                )

                # Update KPIs, site status, feed, and audit table
                breaches, critical, frames, avg_fps, score, dur_str = compute_kpis()
                render_kpis(breaches, critical, st.session_state.total_frames_scanned, fps, score, dur_str)
                with status_ph:
                    draw_site_status(breaches, critical)
                with sys_status_ph:
                    draw_system_status(DB_AVAILABLE, True)

                # Update live violation feed
                with feed_ph:
                    if st.session_state.session_rows:
                        recent = st.session_state.session_rows[-10:]
                        for r in reversed(recent):
                            draw_violation_feed_card(
                                timestamp=r[0].split(" ")[1],
                                violation_type=r[2],
                                worker_id=r[1],
                                confidence=float(r[3]),
                                severity=severity_for(r[2]),
                                status=r[9],
                            )
                    else:
                        st.markdown('<div style="padding:16px;text-align:center;color:var(--text-muted);font-size:0.78rem;">Scanning… No violations detected yet.</div>', unsafe_allow_html=True)

                # Update audit log table
                if st.session_state.session_rows:
                    df = pd.DataFrame(st.session_state.session_rows, columns=CSV_HEADER)
                    df["severity"] = df["violation_type"].apply(severity_for)
                    logs_ph.dataframe(
                        df[["timestamp", "worker_id", "violation_type", "severity", "confidence", "status"]],
                        use_container_width=True,
                    )



# ─────────────────────────────────────────────────────────────────────────────
#  DETECTION ENGINE — NATIVE CAMERA INPUT (BUILT-IN STREAMLIT WEBCAM)
# ─────────────────────────────────────────────────────────────────────────────
elif video_source == "Native Camera (Snapshot/Stream)":
    if st.session_state.running:
        with st.spinner("⛑ Loading AEGIS detection model…"):
            detector = _load_detector(confidence_slider)
        with cctv_header_ph:
            render_cctv_hud_header(source_name=video_source, is_live=True, fps_val=1.0)

        with video_ph.container():
            cam_buffer = st.camera_input("📷 Real-Time Camera Stream / Snapshot", key="native_webcam_input")

        if cam_buffer is not None:
            raw_bytes = cam_buffer.getvalue()
            pil_img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            frame = np.array(pil_img)

            st.session_state.total_frames_scanned += 1
            annotated, detections = detector.detect(frame, line_width=line_thickness,
                                                    alert_classes=alert_classes)
            st.session_state.last_annotated_frame = annotated

            rects       = [d["bbox"] for d in detections]
            class_names = [d["class_name"] for d in detections]

            if not st.session_state.tracker:
                st.session_state.tracker = CentroidTracker()
            tracker      = st.session_state.tracker
            assigned_ids = tracker.update(rects, class_names)

            for idx, d in enumerate(detections):
                if d["class_name"] in alert_classes:
                    w_id = assigned_ids[idx] if idx < len(assigned_ids) else "Unknown"
                    log_violation(tracker, w_id, d,
                                  st.session_state.total_frames_scanned, annotated)

            # Display annotated result below camera input
            with video_ph.container():
                st.image(annotated, caption="🔍 Real-Time AI Inference Result", use_container_width=True)

            breaches, critical, frames, avg_fps, score, dur_str = compute_kpis()
            render_kpis(breaches, critical, st.session_state.total_frames_scanned, 1.0, score, dur_str)
            with status_ph:
                draw_site_status(breaches, critical)
            with sys_status_ph:
                draw_system_status(DB_AVAILABLE, True)


# ─────────────────────────────────────────────────────────────────────────────
#  DETECTION ENGINE — VIDEO / LOCAL WEBCAM (OPENCV)
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.running:
    if not CV2_OK:
        err_detail = f": {_CV2_ERR_MSG}" if _CV2_ERR_MSG else ""
        st.error(f"⚠️ Video file decoding requires OpenCV{err_detail}. "
                 "Please switch video source to 'Laptop Camera (Browser)' which runs directly without OpenCV.")
        st.session_state.running = False
        st.stop()
    detector = _load_detector(confidence_slider)
    if not st.session_state.get("_model_warm"):
        with st.spinner("⛑ Loading AEGIS detection model — this takes ~20 s on first run…"):
            detector = _load_detector(confidence_slider)
        st.session_state["_model_warm"] = True

    # Resolve capture source
    cap_src = None
    if video_source == "Sample Video" and sample_video:
        cap_src = sample_video
    elif video_source == "Upload Video File":
        if uploaded_file:
            tmp = tempfile.NamedTemporaryFile(
                delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
            tmp.write(uploaded_file.read())
            tmp.close()
            cap_src = tmp.name
        else:
            st.warning("Please upload a video file to begin.")
            st.session_state.running = False
            st.stop()
    elif video_source == "Local Webcam (OpenCV)":
        cap_src = int(st.session_state.get("adv_cam_idx", 0))

    if cap_src is None:
        if sample_video:
            cap_src = sample_video
            st.info("Using sample video for demonstration.")
        else:
            st.warning("Please upload a video file or select a valid source.")
            st.session_state.running = False
            st.stop()

    # Open capture
    cap = None
    if isinstance(cap_src, int):
        if use_dshow:
            cap = cv2.VideoCapture(cap_src, cv2.CAP_DSHOW)
        if cap is None or not cap.isOpened():
            cap = cv2.VideoCapture(cap_src)
    else:
        cap = cv2.VideoCapture(cap_src)

    if not cap.isOpened() and cap_src != sample_video and sample_video:
        st.info("Local webcam not available. Falling back to sample video.")
        cap = cv2.VideoCapture(sample_video)

    if not cap.isOpened():
        st.error(f"Unable to open video stream from source (index: {cap_src}). Please ensure camera is connected and not occupied by another app.")
        st.session_state.running = False
        st.stop()

    local_run_id = st.session_state.current_run_id
    prev_time    = time.time()
    total_frames = st.session_state.total_frames_scanned
    fps_history  = deque(list(st.session_state.fps_history),  maxlen=60)
    time_history = deque(list(st.session_state.time_history), maxlen=60)

    if not st.session_state.tracker:
        st.session_state.tracker = CentroidTracker()
    tracker = st.session_state.tracker

    try:
        while cap.isOpened() and st.session_state.running:
            if local_run_id != st.session_state.current_run_id:
                break

            ret, frame = cap.read()
            if not ret:
                break

            total_frames += 1
            st.session_state.total_frames_scanned = total_frames

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # ── Performance: cap resolution on cloud before inference ─────────
            if _IS_CLOUD:
                rgb = cv2.resize(rgb, (640, 480))

            # ── Performance: skip inference on even frames on cloud ───────────
            if _IS_CLOUD and total_frames % 2 == 0:
                if "last_annotated_frame" in st.session_state and st.session_state.last_annotated_frame is not None:
                    if total_frames % 6 == 0:  # still refresh display every 6 frames
                        refresh_ui(st.session_state.last_annotated_frame, fps,
                                   total_frames, fps_history, time_history)
                continue

            annotated, detections = detector.detect(rgb, line_width=line_thickness,
                                                    alert_classes=alert_classes)
            st.session_state.last_annotated_frame = annotated


            rects       = [d["bbox"] for d in detections]
            class_names = [d["class_name"] for d in detections]
            assigned_ids = tracker.update(rects, class_names)

            for idx, d in enumerate(detections):
                if d["class_name"] in alert_classes:
                    w_id = assigned_ids[idx] if idx < len(assigned_ids) else "Unknown"
                    log_violation(tracker, w_id, d, total_frames, annotated)

            # FPS
            now = time.time()
            fps = 1.0 / max(1e-6, now - prev_time)
            prev_time = now
            fps_history.append(fps)
            time_history.append(datetime.now().strftime("%H:%M:%S"))
            st.session_state.fps_history  = list(fps_history)
            st.session_state.time_history = list(time_history)

            # Render every 3 frames to reduce overhead
            if total_frames % 3 == 0 or total_frames == 1:
                refresh_ui(annotated, fps, total_frames, fps_history, time_history)

            time.sleep(0.005)

    finally:
        cap.release()
        # Mark DB session complete
        if st.session_state.db_session_id is not None:
            close_scan_session(
                st.session_state.db_session_id,
                total_frames=st.session_state.total_frames_scanned,
                total_violations=len(st.session_state.session_rows),
                status="completed",
            )
        st.session_state.running = False
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  STANDBY / POST-SCAN STATE
# ─────────────────────────────────────────────────────────────────────────────
else:
    if st.session_state.session_rows:
        # ── Post-scan summary ──────────────────────────────────────────────
        rows     = st.session_state.session_rows
        frames   = st.session_state.total_frames_scanned
        breaches = len(rows)
        critical = sum(1 for r in rows if severity_for(r[2]) == "CRITICAL")

        elapsed = 0.0
        if st.session_state.scan_start_time:
            elapsed = time.time() - st.session_state.scan_start_time
        dur_str = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}"

        with cctv_header_ph:
            render_cctv_hud_header(source_name=video_source, is_live=False, fps_val=0.0)
        with video_ph:
            scan_complete_placeholder(breaches, frames, dur_str)


        render_kpis(breaches, critical, frames,
                    (sum(st.session_state.fps_history) / len(st.session_state.fps_history)
                     if st.session_state.fps_history else 0),
                    max(0, round((1 - breaches / max(frames, 1)) * 100, 1)),
                    dur_str)

        with status_ph:
            draw_site_status(breaches, critical)

        with sys_status_ph:
            draw_system_status(DB_AVAILABLE, False)

        # Perf chart from history
        perf_ph.plotly_chart(
            _perf_chart(st.session_state.fps_history, st.session_state.time_history,
                        key="post_scan"),
            use_container_width=True,
            config={"displayModeBar": False},
            key="post_scan_perf",
        )

        with feed_ph:
            recent = rows[-5:]
            for r in reversed(recent):
                draw_violation_feed_card(
                    timestamp=r[0].split(" ")[1],
                    violation_type=r[2],
                    worker_id=r[1],
                    confidence=float(r[3]),
                    severity=severity_for(r[2]),
                    status=r[9],
                )

        df = pd.DataFrame(rows, columns=CSV_HEADER)
        df["severity"] = df["violation_type"].apply(severity_for)
        logs_ph.dataframe(
            df[["timestamp", "worker_id", "violation_type", "severity", "confidence", "status"]],
            use_container_width=True,
        )

        st.download_button(
            "Download violation report (CSV)",
            data=df.to_csv(index=False),
            file_name=f"aegis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    else:
        # ── Initial standby ────────────────────────────────────────────────
        render_kpis(0, 0, 0, 0, 100.0, "00:00")
        with cctv_header_ph:
            render_cctv_hud_header(source_name=video_source, is_live=False, fps_val=0.0)
        with video_ph:
            standby_placeholder(DB_AVAILABLE)
        with status_ph:
            draw_site_status(0, 0)
        draw_empty_perf()

