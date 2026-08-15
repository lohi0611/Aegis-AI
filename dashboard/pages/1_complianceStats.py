"""
AEGIS Safety Intelligence — Compliance & Analytics
Reads from the persistent SQLite/PostgreSQL database.
Falls back to CSV if DB is unavailable.
"""
import os
import csv
from datetime import datetime, date, timedelta

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from ui_utils import apply_custom_css, mission_control_header, kpi_card, navigation_tip
from db import DB_AVAILABLE, get_analytics, get_recent_sessions, get_session_violations

st.set_page_config(
    page_title="AEGIS | Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_bar="expanded",
)
apply_custom_css()

# ── Colors ───────────────────────────────────────────────────────────────────
ORANGE = "#f97316"; RED = "#ef4444"; GREEN = "#22c55e"; TEAL = "#06b6d4"; AMBER = "#fbbf24"

# ── Header ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 10px;">
        <div style="font-size:2.2rem;filter:drop-shadow(0 0 10px rgba(249,115,22,0.4));">⛑️</div>
        <div style="font-size:0.95rem;font-weight:800;color:#fff;letter-spacing:2px;">AEGIS AI</div>
        <div style="font-size:0.6rem;color:rgba(241,245,249,0.3);text-transform:uppercase;
            letter-spacing:2px;margin-top:2px;">Safety Intelligence</div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(249,115,22,0.2),transparent);
        margin:4px 0 14px;"></div>
    """, unsafe_allow_html=True)
    navigation_tip()

mission_control_header(
    "📊 SAFETY ANALYTICS",
    "Historical compliance metrics & violation patterns",
)

# ── Load data ─────────────────────────────────────────────────────────────────
analytics = get_analytics() if DB_AVAILABLE else {}
sessions  = get_recent_sessions(30) if DB_AVAILABLE else []

# CSV fallback for violations history
current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
csv_path = next(
    (p for p in [
        os.path.join(project_root, "violations.csv"),
        os.path.join(current_dir,  "violations.csv"),
    ] if os.path.exists(p)),
    None,
)

def load_csv_df():
    if csv_path and os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            return df.dropna(subset=["timestamp"])
        except Exception:
            pass
    return pd.DataFrame()

csv_df = load_csv_df()


# ── DB unavailable warning ─────────────────────────────────────────────────────
if not DB_AVAILABLE:
    st.markdown("""
    <div class="warning-stripe">
        ⚠️ <b>Database offline</b> — analytics are sourced from the CSV fallback.
        Install <code>sqlalchemy</code> and restart for full persistent analytics.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")


# ── KPI Banner ────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)

total_scans      = analytics.get("total_scans", 0)      if DB_AVAILABLE else (len(sessions) or (len(csv_df) if not csv_df.empty else 0))
total_violations = analytics.get("total_violations", 0) if DB_AVAILABLE else (len(csv_df) if not csv_df.empty else 0)
violations_today = analytics.get("violations_today", 0) if DB_AVAILABLE else (
    len(csv_df[csv_df["timestamp"].dt.date == date.today()]) if not csv_df.empty else 0
)
critical_v       = analytics.get("critical_violations", 0) if DB_AVAILABLE else 0
most_common      = analytics.get("most_common", "N/A")     if DB_AVAILABLE else (
    csv_df["violation_type"].value_counts().idxmax() if not csv_df.empty and "violation_type" in csv_df else "N/A"
)
safety_score     = analytics.get("safety_score", 100.0)   if DB_AVAILABLE else 100.0

with c1: kpi_card("Total Scans",       str(total_scans),       "📹", TEAL)
with c2: kpi_card("Total Violations",  str(total_violations),  "🚨", RED if total_violations > 0 else GREEN)
with c3: kpi_card("Today's Violations",str(violations_today),  "📅", AMBER if violations_today > 0 else GREEN)
with c4: kpi_card("Critical Events",   str(critical_v),        "🔥", RED if critical_v > 0 else GREEN)
with c5: kpi_card("Most Common",       most_common[:15] if most_common != "N/A" else "N/A", "📌", ORANGE)
with c6: kpi_card("Safety Score",      f"{safety_score}%",     "🛡️",
                   GREEN if safety_score >= 80 else AMBER if safety_score >= 50 else RED)

st.markdown("---")


# ── Charts ─────────────────────────────────────────────────────────────────────
ch1, ch2 = st.columns(2)

with ch1:
    st.markdown('<div class="section-title">📊 Violations by Type</div>', unsafe_allow_html=True)
    by_type = analytics.get("by_type", {}) if DB_AVAILABLE else {}
    if not by_type and not csv_df.empty and "violation_type" in csv_df:
        by_type = csv_df["violation_type"].value_counts().to_dict()

    if by_type:
        colors_map = {
            "NO-Hardhat":      RED,
            "NO-Safety Vest":  RED,
            "NO-Mask":         AMBER,
        }
        bar_colors = [colors_map.get(k, TEAL) for k in by_type]
        fig = go.Figure(go.Bar(
            x=list(by_type.keys()),
            y=list(by_type.values()),
            marker_color=bar_colors,
            marker_line_color="rgba(255,255,255,0.05)",
            marker_line_width=1,
        ))
        fig.update_layout(
            height=280, margin=dict(l=10, r=10, t=10, b=40),
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(size=11, color="rgba(241,245,249,0.5)")),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No violation data yet.")

with ch2:
    st.markdown('<div class="section-title">📈 Violations Over Time</div>', unsafe_allow_html=True)
    daily = analytics.get("daily", []) if DB_AVAILABLE else []
    if not daily and not csv_df.empty and "timestamp" in csv_df:
        gd = csv_df.groupby(csv_df["timestamp"].dt.date).size().reset_index()
        gd.columns = ["date", "count"]
        daily = [{"date": str(r["date"]), "count": r["count"]} for _, r in gd.iterrows()]

    if daily:
        dates  = [d["date"] for d in daily]
        counts = [d["count"] for d in daily]
        fig = go.Figure(go.Scatter(
            x=dates, y=counts,
            mode="lines+markers",
            line=dict(color=ORANGE, width=2),
            marker=dict(color=ORANGE, size=5),
            fill="tozeroy",
            fillcolor="rgba(249,115,22,0.07)",
        ))
        fig.update_layout(
            height=280, margin=dict(l=10, r=10, t=10, b=40),
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(size=10, color="rgba(241,245,249,0.5)"),
                       tickangle=-30),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No timeline data yet.")

st.markdown("---")


# ── Session History ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🗂️ Scan Session History</div>', unsafe_allow_html=True)

if sessions:
    for s in sessions:
        status_col = GREEN if s["status"] == "completed" else ORANGE if s["status"] == "running" else AMBER
        dur = f"{int(s['duration_seconds'] or 0)}s" if s["duration_seconds"] else "—"
        end = s["end_time"][:19] if s["end_time"] else "—"

        with st.expander(
            f"📹 Session #{s['session_id']} — {s['scan_type'].replace('_',' ').title()} | "
            f"{s['total_violations']} violations | {s['start_time'][:19] if s['start_time'] else ''}",
            expanded=False
        ):
            ic1, ic2, ic3, ic4, ic5 = st.columns(5)
            with ic1: kpi_card("Source",     s["source_name"] or "—",      "📁", TEAL)
            with ic2: kpi_card("Start",      s["start_time"][:16] if s["start_time"] else "—", "🕐", TEAL)
            with ic3: kpi_card("End",        end[:16],                      "🏁", TEAL)
            with ic4: kpi_card("Duration",   dur,                           "⏱️", ORANGE)
            with ic5: kpi_card("Violations", str(s["total_violations"]),    "🚨",
                                RED if s["total_violations"] > 0 else GREEN)

            # Load violations for this session
            v_list = get_session_violations(s["session_id"])
            if v_list:
                df_v = pd.DataFrame(v_list)
                st.dataframe(
                    df_v[["timestamp", "worker_id", "violation_type", "severity",
                           "confidence", "frame_number", "status"]],
                    use_container_width=True,
                )
                st.download_button(
                    f"⬇️ Download Session #{s['session_id']} CSV",
                    data=df_v.to_csv(index=False),
                    file_name=f"aegis_session_{s['session_id']}.csv",
                    mime="text/csv",
                    key=f"dl_{s['session_id']}",
                )
            else:
                st.info("No violation records for this session.")
elif not csv_df.empty:
    st.info("DB offline — showing last 30 rows from CSV fallback.")
    st.dataframe(csv_df.tail(30), use_container_width=True)
else:
    st.info("No scan sessions recorded yet. Run a scan to generate data.")