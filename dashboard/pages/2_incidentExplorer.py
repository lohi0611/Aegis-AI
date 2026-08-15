"""
AEGIS Safety Intelligence — Incident Explorer
Browse, filter, and export individual violation records from the database.
"""
import os
from datetime import datetime, date, timedelta

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from ui_utils import (
    apply_custom_css, mission_control_header, kpi_card,
    navigation_tip, render_theme_toggle, section_label,
    get_plotly_layout_defaults, ICONS, ORANGE, RED, GREEN, TEAL, AMBER,
)
from db import DB_AVAILABLE, get_recent_sessions, get_session_violations, get_analytics

st.set_page_config(
    page_title="AEGIS | Incident Explorer",
    page_icon="⛑",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
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
            <div style="font-size:0.6rem;color:rgba(232,237,242,0.3);letter-spacing:0.5px;">Incident Explorer</div>
        </div>
    </div>
</div>
<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(249,168,37,0.15),transparent);margin:0 0 8px;"></div>
<div style="padding:0 16px;">
""", unsafe_allow_html=True)
    render_theme_toggle(key="theme_toggle_sidebar")
    navigation_tip()
    st.markdown("</div>", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
hdr_l, hdr_r = st.columns([10, 1])
with hdr_l:
    mission_control_header("Incident Explorer", "Drill into individual violation events and session records")
with hdr_r:
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    render_theme_toggle(key="theme_toggle_header")

if not DB_AVAILABLE:
    st.markdown("""
<div class="warning-stripe">
    Database offline — reading from CSV fallback. Install <code>sqlalchemy</code>
    and restart for full database-backed explorer.
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
    st.markdown("""<div style="padding:40px;text-align:center;color:var(--text-muted);font-size:0.8rem;
        background:var(--bg-card-2);border-radius:var(--r);border:1px solid var(--border-subtle);">
        No scan sessions found. Run a scan on the Safety Monitor page to generate data.
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Session selector ──────────────────────────────────────────────────────────
section_label("Select session", "camera")

session_options = {
    f"Session #{s['session_id']} — {s['scan_type'].replace('_',' ').title()} | "
    f"{s['start_time'][:16] if s['start_time'] else ''} | {s['total_violations']} violations": s
    for s in sessions
}

chosen_label = st.selectbox("Select a scan session to explore:", list(session_options.keys()))
chosen = session_options[chosen_label]

# ── Session summary KPIs ──────────────────────────────────────────────────────
st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
section_label("Session overview", "activity")

dur = f"{int(chosen['duration_seconds'] or 0)}s" if chosen["duration_seconds"] else "—"
sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
with sc1: kpi_card("Session ID",  f"#{chosen['session_id']}",             "database",  "kpi-teal")
with sc2: kpi_card("Scan type",   chosen["scan_type"].replace("_"," ").title(), "camera", "kpi-teal")
with sc3: kpi_card("Source",      (chosen["source_name"] or "—")[:16],    "eye",       "kpi-yellow")
with sc4: kpi_card("Duration",    dur,                                     "clock",     "kpi-yellow")
with sc5: kpi_card("Violations",  str(chosen["total_violations"]),         "alert-triangle",
                    "kpi-red" if chosen["total_violations"] > 0 else "kpi-green")
with sc6: kpi_card("Status",      chosen["status"].capitalize(),           "check-circle",
                    "kpi-green" if chosen["status"] == "completed" else "kpi-yellow")

# ── Load violations for chosen session ────────────────────────────────────────
v_list = get_session_violations(chosen["session_id"])

if not v_list:
    st.markdown("""<div style="padding:24px;text-align:center;color:var(--text-muted);font-size:0.8rem;
        background:var(--bg-card-2);border-radius:var(--r);border:1px solid var(--border-subtle);margin-top:16px;">
        No violation records logged for this session.
    </div>""", unsafe_allow_html=True)
    st.stop()

df = pd.DataFrame(v_list)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# ── Also merge any in-memory rows from the CURRENT session that may not have
#    been committed to DB yet (happens if DB write lagged or failed) ──────────
_mem_rows = st.session_state.get("session_rows", [])
_current_db_sid = st.session_state.get("db_session_id")
if _mem_rows and _current_db_sid == chosen["session_id"] and df.empty:
    from db import DB_AVAILABLE as _dba  # noqa
    _col_names = ["timestamp", "worker_id", "violation_type", "confidence",
                  "x1", "y1", "x2", "y2", "snapshot_path", "status"]
    df = pd.DataFrame(_mem_rows, columns=_col_names)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["violation_id"] = range(1, len(df) + 1)
    df["severity"] = df["violation_type"].apply(
        lambda v: "CRITICAL" if ("Hardhat" in v or "Vest" in v) else "HIGH")
    df["frame_number"] = 0

st.markdown('<hr>', unsafe_allow_html=True)

# ── Filters ───────────────────────────────────────────────────────────────────
section_label("Filter incidents", "eye")
fc1, fc2, fc3 = st.columns(3)

with fc1:
    types = ["All"] + sorted(df["violation_type"].unique().tolist())
    sel_type = st.selectbox("Violation type", types, key="explorer_type")

with fc2:
    severities = ["All", "CRITICAL", "HIGH", "MEDIUM"]
    sel_sev = st.selectbox("Severity level", severities, key="explorer_sev")

with fc3:
    workers = ["All"] + sorted(df["worker_id"].dropna().unique().tolist())
    sel_worker = st.selectbox("Worker identifier", workers, key="explorer_worker")

# Apply filters
fdf = df.copy()
if sel_type   != "All": fdf = fdf[fdf["violation_type"] == sel_type]
if sel_sev    != "All": fdf = fdf[fdf["severity"]       == sel_sev]
if sel_worker != "All": fdf = fdf[fdf["worker_id"]      == sel_worker]

st.markdown(f"""
<div style="font-size:0.75rem;color:var(--text-muted);margin:4px 0 14px;">
    Showing <b style="color:var(--accent);">{len(fdf)}</b> of {len(df)} recorded incidents
</div>
""", unsafe_allow_html=True)

# ── Mini charts ───────────────────────────────────────────────────────────────
mc1, mc2 = st.columns(2)
layout_kw = get_plotly_layout_defaults()

with mc1:
    section_label("Distribution by type", "alert-triangle")
    type_counts = fdf["violation_type"].value_counts()
    if not type_counts.empty:
        bar_colors = [RED if ("Hardhat" in k or "Vest" in k) else AMBER for k in type_counts.index]
        fig = go.Figure(go.Bar(
            x=type_counts.index.tolist(),
            y=type_counts.values.tolist(),
            marker_color=bar_colors,
            marker_line_width=0,
        ))
        fig.update_layout(
            height=200, margin=dict(l=5, r=5, t=5, b=30),
            showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True),
            **{k: v for k, v in layout_kw.items() if k not in ("xaxis", "yaxis")},
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No data matching current filters.")

with mc2:
    section_label("Incident timeline", "clock")
    if not fdf.empty and "timestamp" in fdf:
        tdf = fdf.set_index("timestamp").resample("1min")["violation_id"].count().reset_index() \
              if "violation_id" in fdf.columns else \
              fdf.set_index("timestamp").resample("1min").size().reset_index(name="violation_id")
        tdf.columns = ["time", "count"]
        fig = go.Figure(go.Scatter(
            x=tdf["time"], y=tdf["count"],
            mode="lines+markers",
            line=dict(color=ORANGE, width=2),
            marker=dict(color=ORANGE, size=4),
            fill="tozeroy", fillcolor="rgba(249,168,37,0.06)",
        ))
        fig.update_layout(
            height=200, margin=dict(l=5, r=5, t=5, b=30),
            showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(size=9), tickangle=-20),
            yaxis=dict(showgrid=True),
            **{k: v for k, v in layout_kw.items() if k not in ("xaxis", "yaxis")},
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No timeline data available.")

st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

# ── Violation Table ────────────────────────────────────────────────────────────
section_label("Recorded incidents", "database")

cols_to_show = ["timestamp", "worker_id", "violation_type", "severity",
                "confidence", "frame_number", "status"]
available = [c for c in cols_to_show if c in fdf.columns]
st.dataframe(fdf[available].sort_values("timestamp", ascending=False),
             use_container_width=True)

# ── Snapshot Gallery ──────────────────────────────────────────────────────────
if "snapshot_path" in fdf.columns:
    snap_rows = fdf[fdf["snapshot_path"].notna() & (fdf["snapshot_path"] != "")]
    if not snap_rows.empty:
        section_label("Violation snapshots", "camera")
        st.markdown(
            '<div style="font-size:0.72rem;color:var(--text-muted);margin-bottom:10px;">'
            'Annotated frames captured at the moment of each logged violation.</div>',
            unsafe_allow_html=True,
        )
        snap_sample = snap_rows.sort_values("timestamp", ascending=False).head(12)
        cols_per_row = 4
        rows_iter = [snap_sample.iloc[i:i+cols_per_row]
                     for i in range(0, len(snap_sample), cols_per_row)]
        for row_chunk in rows_iter:
            img_cols = st.columns(cols_per_row)
            for col_idx, (_, snap_row) in enumerate(row_chunk.iterrows()):
                snap_path = snap_row["snapshot_path"]
                with img_cols[col_idx]:
                    if snap_path and os.path.isfile(str(snap_path)):
                        ts_label = str(snap_row["timestamp"])[:19] if snap_row["timestamp"] is not None else ""
                        worker_label = snap_row.get("worker_id", "")
                        v_type = snap_row.get("violation_type", "")
                        st.image(str(snap_path),
                                 caption=f"{worker_label} — {v_type}\n{ts_label}",
                                 use_container_width=True)
                    else:
                        st.markdown(
                            '<div style="height:100px;display:flex;align-items:center;'
                            'justify-content:center;background:var(--bg-card-2);border-radius:6px;'
                            'border:1px solid var(--border-subtle);color:var(--text-muted);'
                            'font-size:0.7rem;">Image not available</div>',
                            unsafe_allow_html=True,
                        )

# ── Download ──────────────────────────────────────────────────────────────────
st.download_button(
    "Download filtered records (CSV)",
    data=fdf.to_csv(index=False),
    file_name=f"aegis_incidents_session{chosen['session_id']}.csv",
    mime="text/csv",
)

