import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent))
from etl.load import load_table

st.set_page_config(page_title="CampusPulse", page_icon="📊", layout="wide")

# load all tables from db
@st.cache_data
def get_data():
    preds   = load_table("predictions")
    weekly  = load_table("weekly_workload")
    asgn    = load_table("assignments")
    shifts  = load_table("shifts")

    preds["week_start"]  = pd.to_datetime(preds["week_start"])
    weekly["week_start"] = pd.to_datetime(weekly["week_start"])
    asgn["due_date"]     = pd.to_datetime(asgn["due_date"])
    shifts["date"]       = pd.to_datetime(shifts["date"])

    metrics = {}
    mp = Path("data/processed/metrics.json")
    if mp.exists():
        metrics = json.loads(mp.read_text())

    return preds, weekly, asgn, shifts, metrics

preds, weekly, asgn, shifts, metrics = get_data()

st.title("CampusPulse - Workload Analytics")
st.caption("Spring 2025 Semester")
st.divider()

# top stats
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("High-Risk Weeks",   f"{int(preds['predicted'].sum())} / {len(preds)}")
c2.metric("Avg Risk",          f"{round(preds['risk_score'].mean()*100, 1)}%")
c3.metric("Total Assignments", len(asgn))
c4.metric("Total Work Hours",  f"{round(shifts['hours_worked'].sum(), 1)} hrs")
c5.metric("Model AUC (CV)",    metrics.get("cv_auc_mean", "N/A"))

st.divider()

# workload timeline + risk score
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Weekly Workload & Risk Score")

    # color bars by risk level
    colors = preds["risk_score"].apply(
        lambda r: "crimson" if r >= 0.65 else ("orange" if r >= 0.35 else "steelblue")
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=preds["week_start"],
        y=preds["total_workload_hours"],
        name="Total Hours",
        marker_color=colors,
        opacity=0.8,
    ))
    fig.add_trace(go.Scatter(
        x=preds["week_start"],
        y=preds["risk_score"] * preds["total_workload_hours"].max(),
        name="Risk Score (scaled)",
        mode="lines+markers",
        line=dict(color="black", width=2, dash="dot"),
        yaxis="y2",
    ))
    fig.update_layout(
        yaxis=dict(title="Hours"),
        yaxis2=dict(title="Risk Score", overlaying="y", side="right", range=[0, 1]),
        legend=dict(orientation="h", y=-0.2),
        hovermode="x unified",
        height=360,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Risk Distribution")
    risk_counts = preds["risk_level"].value_counts().reset_index()
    risk_counts.columns = ["Risk Level", "Weeks"]
    colors_map = {"Low": "#2196F3", "Medium": "#FF9800", "High": "#F44336"}
    fig2 = px.pie(risk_counts, names="Risk Level", values="Weeks",
                  color="Risk Level", color_discrete_map=colors_map, hole=0.45)
    fig2.update_layout(height=300, margin=dict(t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# assignment heatmap + shift bars
col3, col4 = st.columns(2)

with col3:
    st.subheader("Assignments Due per Week (by Course)")
    asgn_w = asgn.copy()
    asgn_w["week_start"] = asgn_w["due_date"] - pd.to_timedelta(asgn_w["due_date"].dt.dayofweek, unit="D")
    pivot = asgn_w.groupby(["week_start", "course"]).size().unstack(fill_value=0)
    fig3 = px.imshow(pivot.T, color_continuous_scale="Blues", aspect="auto",
                     labels=dict(x="Week", y="Course", color="Count"))
    fig3.update_layout(height=280, margin=dict(t=10, b=10))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Work Hours per Week")
    shifts_w = shifts.copy()
    shifts_w["week_start"] = shifts_w["date"] - pd.to_timedelta(shifts_w["date"].dt.dayofweek, unit="D")
    s_agg = shifts_w.groupby("week_start")["hours_worked"].sum().reset_index()
    fig4 = px.bar(s_agg, x="week_start", y="hours_worked", color="hours_worked",
                  color_continuous_scale="Oranges",
                  labels={"hours_worked": "Hours", "week_start": "Week"})
    fig4.update_layout(height=280, margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# feature importances + weekly table
col5, col6 = st.columns([2, 3])

with col5:
    st.subheader("Top Predictive Features")
    if metrics.get("top_features"):
        feat_df = pd.DataFrame(metrics["top_features"][:8])
        fig5 = px.bar(feat_df, x="importance", y="feature", orientation="h",
                      color="importance", color_continuous_scale="Viridis")
        fig5.update_layout(height=300, margin=dict(t=10, b=10),
                           yaxis=dict(autorange="reversed"),
                           coloraxis_showscale=False)
        st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("Week by Week Breakdown")
    display = preds.copy()
    display["week_start"]  = display["week_start"].dt.strftime("%b %d")
    display["risk_score"]  = (display["risk_score"] * 100).round(1).astype(str) + "%"
    display["has_exam"]    = display["has_exam"].apply(lambda x: "Yes" if x else "No")
    display = display.rename(columns={
        "week_start":           "Week",
        "total_workload_hours": "Total Hrs",
        "assignments_due":      "Assignments",
        "shift_hours":          "Work Hrs",
        "has_exam":             "Exam?",
        "risk_score":           "Risk %",
        "risk_level":           "Level",
    })
    st.dataframe(
        display[["Week", "Total Hrs", "Assignments", "Work Hrs", "Exam?", "Risk %", "Level"]],
        use_container_width=True,
        height=300,
    )

st.caption(
    f"Model: GradientBoostingClassifier | "
    f"CV F1: {metrics.get('cv_f1_mean','N/A')} | "
    f"CV AUC: {metrics.get('cv_auc_mean','N/A')}"
)
