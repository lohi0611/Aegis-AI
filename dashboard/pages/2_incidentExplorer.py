"""
AEGIS Safety Intelligence — Incident Explorer
Browse, filter, and export individual violation records from the DB.
"""
import os
from datetime import datetime, date, timedelta

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from ui_utils import apply_custom_css, mission_control_header, kpi_card, navigation_tip
from db import DB_AVAILABLE, get_recent_sessions, get_session_violations, get_analytics

st.set_page_config(
    page_title="AEGIS | Incident Explorer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_bar="expanded",
)
apply_custom_css()

ORANGE = "#f97316"; RED = "#ef4444"; GREEN = "#22c55e"; TEAL = "#06b6d4"; AMBER = "#fbbf24"

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 10px;">
        <div style="font-size:2.2rem;filter:drop-shadow(0 0 10px rgba(249,115,22,0.4));">⛑️</div>
        <div style="font-size:0.95rem;font-weight:800;color:#fff;letter-spacing:2px;">AEGIS AI</div>
        <div style="font-size:0.6rem;color:rgba(241,245,249,0.3);text-transform:uppercase;
            letter-spacing:2px;margin-top:2px;">Incident Explorer</div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(249,115,22,0.2),transparent);
        margin:4px 0 14px;"></div>
    """, unsafe_allow_html=True)
    navigation_tip()

mission_control_header(
    "🔍 INCIDENT EXPLORER",
    "Drill into individual violation events and session records",
)

if not DB_AVAILABLE:
    st.markdown("""
    <div class="warning-stripe">
        ⚠️ <b>Database offline</b> — reading from CSV fallback. Install <code>sqlalchemy</code>
        and restart for full DB-backed explorer.
    </div>
    """, unsafe_allow_html=True)
    # CSV fallback
    current_dir  = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    csv_path = next(
        (p for p in [
            os.path.join(project_root, "violations.csv"),
            os.path.join(os.path.dirname(current_dir), "violations.csv"),
        ] if os.path.exists(p)),
        None,
    )
    if csv_path:
        df = pd.read_csv(csv_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No violation data found.")
    st.stop()

# ── Load sessions ─────────────────────────────────────────────────────────────
sessions = get_recent_sessions(50)

if not sessions:
    st.info("No scan sessions found. Run a scan on the main page to generate data.")
    st.stop()

# ── Session filter ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🗂️ Select Session</div>', unsafe_allow_html=True)

session_options = {
    f"Session #{s['session_id']} — {s['scan_type'].replace('_',' ').title()} | "
    f"{s['start_time'][:16] if s['start_time'] else ''} | {s['total_violations']} violations": s
    for s in sessions
}

chosen_label = st.selectbox("Select a scan session to explore:", list(session_options.keys()))
chosen = session_options[chosen_label]

# ── Session summary KPIs ──────────────────────────────────────────────────────
st.markdown('<div class="section-title" style="margin-top:16px;">📋 Session Summary</div>',
            unsafe_allow_html=True)

dur = f"{int(chosen['duration_seconds'] or 0)}s" if chosen["duration_seconds"] else "—"
sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
with sc1: kpi_card("Session ID",  f"#{chosen['session_id']}",             "🆔",  TEAL)
with sc2: kpi_card("Scan Type",   chosen["scan_type"].replace("_"," ").title(), "📹", TEAL)
with sc3: kpi_card("Source",      (chosen["source_name"] or "—")[:18],    "📁",  ORANGE)
with sc4: kpi_card("Duration",    dur,                                     "⏱️",  ORANGE)
with sc5: kpi_card("Violations",  str(chosen["total_violations"]),         "🚨",
                    RED if chosen["total_violations"] > 0 else GREEN)
with sc6: kpi_card("Status",      chosen["status"].upper(),                "✅",
                    GREEN if chosen["status"] == "completed" else ORANGE)

# ── Load violations for this session ─────────────────────────────────────────
v_list = get_session_violations(chosen["session_id"])

if not v_list:
    st.info("No violation records for this session.")
    st.stop()

df = pd.DataFrame(v_list)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

st.markdown("---")

# ── Filters ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔎 Filter Violations</div>', unsafe_allow_html=True)
fc1, fc2, fc3 = st.columns(3)

with fc1:
    types = ["All"] + sorted(df["violation_type"].unique().tolist())
    sel_type = st.selectbox("Violation Type", types, key="explorer_type")

with fc2:
    severities = ["All", "CRITICAL", "HIGH", "MEDIUM"]
    sel_sev = st.selectbox("Severity", severities, key="explorer_sev")

with fc3:
    workers = ["All"] + sorted(df["worker_id"].dropna().unique().tolist())
    sel_worker = st.selectbox("Worker ID", workers, key="explorer_worker")

# Apply filters
fdf = df.copy()
if sel_type   != "All": fdf = fdf[fdf["violation_type"] == sel_type]
if sel_sev    != "All": fdf = fdf[fdf["severity"]       == sel_sev]
if sel_worker != "All": fdf = fdf[fdf["worker_id"]      == sel_worker]

st.markdown(f"""
<div style="font-size:0.8rem;color:rgba(241,245,249,0.4);margin-bottom:12px;">
    Showing <b style="color:#f97316;">{len(fdf)}</b> of {len(df)} violation records
</div>
""", unsafe_allow_html=True)

# ── Mini charts ───────────────────────────────────────────────────────────────
mc1, mc2 = st.columns(2)

with mc1:
    st.markdown('<div class="section-title">Violations by Type</div>', unsafe_allow_html=True)
    type_counts = fdf["violation_type"].value_counts()
    if not type_counts.empty:
        bar_colors = [RED if "Hardhat" in k or "Vest" in k else AMBER for k in type_counts.index]
        fig = go.Figure(go.Bar(
            x=type_counts.index.tolist(),
            y=type_counts.values.tolist(),
            marker_color=bar_colors,
        ))
        fig.update_layout(
            height=220, margin=dict(l=5, r=5, t=5, b=30),
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(size=10, color="rgba(241,245,249,0.5)")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No data with current filters.")

with mc2:
    st.markdown('<div class="section-title">Violations Timeline</div>', unsafe_allow_html=True)
    if not fdf.empty and "timestamp" in fdf:
        tdf = fdf.set_index("timestamp").resample("1min")["violation_id"].count().reset_index()
        tdf.columns = ["time", "count"]
        fig = go.Figure(go.Scatter(
            x=tdf["time"], y=tdf["count"],
            mode="lines+markers",
            line=dict(color=ORANGE, width=2),
            marker=dict(color=ORANGE, size=5),
            fill="tozeroy", fillcolor="rgba(249,115,22,0.07)",
        ))
        fig.update_layout(
            height=220, margin=dict(l=5, r=5, t=5, b=30),
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(size=9, color="rgba(241,245,249,0.4)"), tickangle=-20),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No timeline data.")

# ── Violation Table ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Violation Records</div>', unsafe_allow_html=True)

cols_to_show = ["timestamp", "worker_id", "violation_type", "severity",
                "confidence", "frame_number", "status"]
available = [c for c in cols_to_show if c in fdf.columns]
st.dataframe(fdf[available].sort_values("timestamp", ascending=False),
             use_container_width=True)

# ── Download ──────────────────────────────────────────────────────────────────
st.download_button(
    "⬇️ Download Filtered Records (CSV)",
    data=fdf.to_csv(index=False),
    file_name=f"aegis_incidents_session{chosen['session_id']}.csv",
    mime="text/csv",
)
