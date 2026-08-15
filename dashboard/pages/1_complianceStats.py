"""
AEGIS Safety Intelligence — Compliance Analytics & Empirical Benchmarks
Historical compliance metrics, violation pattern analysis, and research evaluation metrics.
"""
import os
import json
from datetime import date
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from ui_utils import (
    apply_custom_css, mission_control_header, kpi_card,
    navigation_tip, render_theme_toggle, section_label,
    get_plotly_layout_defaults, ICONS, ORANGE, RED, GREEN, TEAL, AMBER,
)
from db import DB_AVAILABLE, get_analytics, get_recent_sessions, get_session_violations

st.set_page_config(
    page_title="AEGIS | Analytics & Research",
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
            <div style="font-size:0.6rem;color:rgba(232,237,242,0.3);letter-spacing:0.5px;">Safety Intelligence</div>
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
    mission_control_header("Safety Analytics & Research Metrics", "Empirical validation benchmarks, compliance statistics, and session logs")
with hdr_r:
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    render_theme_toggle(key="theme_toggle_header")

# ── DB warning ────────────────────────────────────────────────────────────────
if not DB_AVAILABLE:
    st.markdown("""
<div class="warning-stripe">
    Database offline — analytics sourced from CSV fallback.
    Install <code>sqlalchemy</code> and restart for full persistent analytics.
</div>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
analytics = get_analytics() if DB_AVAILABLE else {}
sessions  = get_recent_sessions(30) if DB_AVAILABLE else []

# CSV fallback
current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
csv_path = next(
    (p for p in [
        os.path.join(project_root, "violations.csv"),
        os.path.join(current_dir,  "violations.csv"),
    ] if os.path.exists(p)), None,
)

def load_csv_df():
    if csv_path:
        try:
            df = pd.read_csv(csv_path)
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            return df.dropna(subset=["timestamp"])
        except Exception:
            pass
    return pd.DataFrame()

csv_df = load_csv_df()

# ── Top KPI banner (Live Session Monitoring) ──────────────────────────────────
total_scans      = analytics.get("total_scans", 0)      if DB_AVAILABLE else len(sessions)
total_violations = analytics.get("total_violations", 0) if DB_AVAILABLE else (len(csv_df) if not csv_df.empty else 0)
violations_today = analytics.get("violations_today", 0) if DB_AVAILABLE else (
    len(csv_df[csv_df["timestamp"].dt.date == date.today()]) if not csv_df.empty else 0)
critical_v       = analytics.get("critical_violations", 0) if DB_AVAILABLE else 0
most_common      = analytics.get("most_common", "N/A") if DB_AVAILABLE else (
    csv_df["violation_type"].value_counts().idxmax() if not csv_df.empty and "violation_type" in csv_df else "N/A")
safety_score     = analytics.get("safety_score", 100.0) if DB_AVAILABLE else 100.0

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1: kpi_card("Total scans",       str(total_scans),       "camera",         "kpi-teal")
with c2: kpi_card("Total violations",  str(total_violations),  "alert-triangle", "kpi-red" if total_violations > 0 else "kpi-green")
with c3: kpi_card("Today's violations",str(violations_today),  "clock",          "kpi-yellow" if violations_today > 0 else "kpi-green")
with c4: kpi_card("Critical events",   str(critical_v),        "x-circle",       "kpi-red" if critical_v > 0 else "kpi-teal")
with c5: kpi_card("Most common",       most_common[:14] if most_common != "N/A" else "N/A", "eye", "kpi-orange")
with c6: kpi_card("Safety score",      f"{safety_score}%",     "shield",
                   "kpi-green" if safety_score >= 80 else ("kpi-yellow" if safety_score >= 50 else "kpi-red"))

st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

# ── Main Tabs: Live Analytics vs Research Evaluation ─────────────────────────
tab_live, tab_research = st.tabs(["📊 Operational Analytics", "🔬 Research & Evaluation Suite"])

layout_kw = get_plotly_layout_defaults()

with tab_live:
    ch1, ch2 = st.columns(2)

    with ch1:
        section_label("Violations by type", "alert-triangle")
        by_type = analytics.get("by_type", {}) if DB_AVAILABLE else {}
        if not by_type and not csv_df.empty and "violation_type" in csv_df:
            by_type = csv_df["violation_type"].value_counts().to_dict()

        if by_type:
            bar_colors = [RED if ("Hardhat" in k or "Vest" in k) else AMBER for k in by_type]
            fig = go.Figure(go.Bar(
                x=list(by_type.keys()), y=list(by_type.values()),
                marker_color=bar_colors, marker_line_width=0,
            ))
            fig.update_layout(
                height=260, margin=dict(l=10, r=10, t=10, b=40),
                showlegend=False,
                xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                yaxis=dict(showgrid=True),
                **{k: v for k, v in layout_kw.items() if k not in ("xaxis", "yaxis")},
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown("""<div style="height:260px;display:flex;align-items:center;justify-content:center;
                color:var(--text-muted);font-size:0.8rem;background:var(--bg-card-2);border-radius:var(--r);
                border:1px solid var(--border-subtle);">No violation data yet.</div>""", unsafe_allow_html=True)

    with ch2:
        section_label("Violations over time", "activity")
        daily = analytics.get("daily", []) if DB_AVAILABLE else []
        if not daily and not csv_df.empty and "timestamp" in csv_df:
            gd = csv_df.groupby(csv_df["timestamp"].dt.date).size().reset_index()
            gd.columns = ["date", "count"]
            daily = [{"date": str(r["date"]), "count": r["count"]} for _, r in gd.iterrows()]

        if daily:
            dates  = [d["date"] for d in daily]
            counts = [d["count"] for d in daily]
            fig = go.Figure(go.Scatter(
                x=dates, y=counts, mode="lines+markers",
                line=dict(color=ORANGE, width=2),
                marker=dict(color=ORANGE, size=5),
                fill="tozeroy", fillcolor="rgba(249,168,37,0.06)",
            ))
            fig.update_layout(
                height=260, margin=dict(l=10, r=10, t=10, b=40),
                showlegend=False,
                xaxis=dict(showgrid=False, tickangle=-30, tickfont=dict(size=9)),
                yaxis=dict(showgrid=True),
                **{k: v for k, v in layout_kw.items() if k not in ("xaxis", "yaxis")},
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown("""<div style="height:260px;display:flex;align-items:center;justify-content:center;
                color:var(--text-muted);font-size:0.8rem;background:var(--bg-card-2);border-radius:var(--r);
                border:1px solid var(--border-subtle);">No timeline data yet.</div>""", unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Session history ───────────────────────────────────────────────────────
    section_label("Scan session history", "database")

    if sessions:
        for s in sessions:
            dur = f"{int(s['duration_seconds'] or 0)}s" if s["duration_seconds"] else "—"
            end = s["end_time"][:16] if s["end_time"] else "—"

            with st.expander(
                f"Session #{s['session_id']} — {s['scan_type'].replace('_',' ').title()} "
                f"| {s['total_violations']} violations | {s['start_time'][:16] if s['start_time'] else ''}",
                expanded=False,
            ):
                ic1, ic2, ic3, ic4, ic5 = st.columns(5)
                with ic1: kpi_card("Source",     s["source_name"] or "—",      "camera", "kpi-teal")
                with ic2: kpi_card("Started",    s["start_time"][:16] if s["start_time"] else "—", "clock", "kpi-teal")
                with ic3: kpi_card("Ended",      end,                           "clock",  "kpi-teal")
                with ic4: kpi_card("Duration",   dur,                           "zap",    "kpi-yellow")
                with ic5: kpi_card("Violations", str(s["total_violations"]),    "alert-triangle",
                                   "kpi-red" if s["total_violations"] > 0 else "kpi-green")

                v_list = get_session_violations(s["session_id"])
                if v_list:
                    df_v = pd.DataFrame(v_list)
                    st.dataframe(
                        df_v[["timestamp", "worker_id", "violation_type", "severity",
                               "confidence", "frame_number", "status"]],
                        use_container_width=True,
                    )
                    st.download_button(
                        f"Download session #{s['session_id']} CSV",
                        data=df_v.to_csv(index=False),
                        file_name=f"aegis_session_{s['session_id']}.csv",
                        mime="text/csv",
                        key=f"dl_{s['session_id']}",
                    )
                else:
                    st.markdown("""<div style="padding:16px;text-align:center;color:var(--text-muted);
                        font-size:0.78rem;">No violation records for this session.</div>""",
                        unsafe_allow_html=True)
    elif not csv_df.empty:
        st.info("Database offline — showing last 30 rows from CSV fallback.")
        st.dataframe(csv_df.tail(30), use_container_width=True)
    else:
        st.markdown("""<div style="padding:40px;text-align:center;color:var(--text-muted);font-size:0.8rem;
            background:var(--bg-card-2);border-radius:var(--r);border:1px solid var(--border-subtle);">
            No scan sessions recorded yet. Run a scan to generate data.
        </div>""", unsafe_allow_html=True)


with tab_research:
    eval_dir = Path(project_root) / "evaluation" / "results"
    summary_json_path = eval_dir / "comprehensive_summary.json"
    
    if summary_json_path.exists():
        try:
            with open(summary_json_path, "r", encoding="utf-8") as f:
                res = json.load(f)
            
            det_m = res.get("detection", {}).get("overall_metrics", {})
            comp_m = res.get("compliance", {}).get("compliance_decision_metrics", {})
            comp_cm = res.get("compliance", {}).get("confusion_matrix", {})
            perf_list = res.get("performance", {}).get("benchmarks_by_resolution", [])

            st.markdown("""
<div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:14px;">
    Empirical quantitative results generated by the dedicated <code>evaluation/</code> module on the Construction Site Safety test split.
</div>""", unsafe_allow_html=True)

            # Quantitative KPI row
            rk1, rk2, rk3, rk4, rk5, rk6 = st.columns(6)
            with rk1: kpi_card("mAP@50 (Detection)", f"{det_m.get('mAP50', 0)*100:.1f}%", "eye", "kpi-teal")
            with rk2: kpi_card("mAP@50-95", f"{det_m.get('mAP50_95', 0)*100:.1f}%", "eye", "kpi-teal")
            with rk3: kpi_card("Compliance Accuracy", f"{comp_m.get('overall_compliance_accuracy', 0)*100:.1f}%", "check-circle", "kpi-green")
            with rk4: kpi_card("Violation Precision", f"{comp_m.get('violation_precision', 0)*100:.1f}%", "shield", "kpi-green")
            with rk5: kpi_card("Violation Recall (Sens.)", f"{comp_m.get('violation_recall_sensitivity', 0)*100:.1f}%", "alert-triangle", "kpi-yellow")
            with rk6: kpi_card("Miss Rate (FNR)", f"{comp_m.get('false_negative_rate_miss_rate', 0)*100:.1f}%", "x-circle", "kpi-red")

            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

            # Two columns: Per-class metrics & Decision Confusion Matrix
            col_rc1, col_rc2 = st.columns(2)

            with col_rc1:
                section_label("Per-Class Detection Metrics", "eye")
                per_class_csv = eval_dir / "detection" / "per_class_metrics.csv"
                if per_class_csv.exists():
                    p_df = pd.read_csv(per_class_csv)
                    st.dataframe(p_df, use_container_width=True)

            with col_rc2:
                section_label("Compliance Decision Confusion Matrix", "check-circle")
                cm_data = [
                    {"Ground Truth": "Violation", "Flagged Violation (Pred)": comp_cm.get("TP_correct_violations", 0), "Flagged Compliant (Pred)": comp_cm.get("FN_missed_hazards", 0)},
                    {"Ground Truth": "Compliant", "Flagged Violation (Pred)": comp_cm.get("FP_false_alarms", 0), "Flagged Compliant (Pred)": comp_cm.get("TN_correct_compliant", 0)},
                ]
                cm_df = pd.DataFrame(cm_data)
                st.dataframe(cm_df, use_container_width=True)

            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

            # Performance Latency Benchmark Table
            section_label("Empirical Latency & FPS Scaling", "zap")
            perf_csv = eval_dir / "performance" / "realtime_benchmark_summary.csv"
            if perf_csv.exists():
                perf_df = pd.read_csv(perf_csv)
                st.dataframe(perf_df, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading research evaluation summary: {e}")
    else:
        st.markdown("""
<div style="padding:40px;text-align:center;color:var(--text-muted);font-size:0.82rem;
    background:var(--bg-card-2);border-radius:var(--r);border:1px solid var(--border-subtle);">
    No research evaluation results found on disk. Run <code>python evaluation/run_all_evaluations.py</code> to generate quantitative metrics.
</div>""", unsafe_allow_html=True)