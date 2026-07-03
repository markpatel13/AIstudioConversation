"""Analytics Dashboard – monitor AI response quality, trends, and improvement."""

import streamlit as st

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

import plotly.express as px
import plotly.graph_objects as go

from components.styles import CUSTOM_CSS, render_sidebar
from utils.api_client import get_client

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    render_sidebar()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<h1 class="page-title">Analytics Dashboard</h1>', unsafe_allow_html=True
)
st.markdown(
    '<p class="page-subtitle">Monitor AI response quality, track trends, and measure improvement</p>',
    unsafe_allow_html=True,
)

client = get_client()
data = client.get_analytics_summary()

if not data:
    st.info(
        "No analytics data available yet. Click **🌱 Seed Demo Data** in the "
        "sidebar to generate sample conversations."
    )
    st.stop()

# ── Plotly theme helper ──────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#FAFAFA", family="Inter"),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA"),
    ),
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
)


# ═══════════════════════════════════════════════════════════════════════════════
# ROW 1 – KPI CARDS
# ═══════════════════════════════════════════════════════════════════════════════
k1, k2, k3, k4 = st.columns(4)

cards = [
    ("💬", "Total Conversations", str(data.get("total_conversations", 0))),
    ("⭐", "Avg Quality", f"{data.get('avg_relevance', 0):.0%}"),
    ("⚠️", "Hallucination Rate", f"{data.get('hallucination_rate', 0):.1f}%"),
    ("👍", "Positive Feedback", f"{data.get('positive_feedback_rate', 0):.1f}%"),
]

for col, (icon, label, value) in zip([k1, k2, k3, k4], cards):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ROW 2 – Quality Trend + Conversations per Day
# ═══════════════════════════════════════════════════════════════════════════════
r2_left, r2_right = st.columns(2)

# ── Response Quality Trend ───────────────────────────────────────────────────
with r2_left:
    st.markdown("#### 📈 Response Quality Trend")
    quality_trend = data.get("quality_trend") or []
    if quality_trend:
        dates = [d.get("date", "") for d in quality_trend]
        relevance_vals = [d.get("avg_relevance", 0) for d in quality_trend]
        groundedness_vals = [d.get("avg_groundedness", 0) for d in quality_trend]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=relevance_vals,
                name="Relevance",
                mode="lines+markers",
                line=dict(shape="spline", width=3, color="#6C63FF"),
                marker=dict(size=7),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=groundedness_vals,
                name="Groundedness",
                mode="lines+markers",
                line=dict(shape="spline", width=3, color="#4ECDC4"),
                marker=dict(size=7),
            )
        )
        fig.update_layout(**CHART_LAYOUT, title=None)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to display quality trends.")

# ── Conversations per Day ────────────────────────────────────────────────────
with r2_right:
    st.markdown("#### 📊 Conversations per Day")
    conv_by_day = data.get("conversations_by_day") or []
    if conv_by_day:
        dates = [d.get("date", "") for d in conv_by_day]
        counts = [d.get("count", 0) for d in conv_by_day]

        fig = go.Figure(
            go.Bar(
                x=dates,
                y=counts,
                marker_color="#6C63FF",
                marker_line_color="#4ECDC4",
                marker_line_width=1.5,
            )
        )
        fig.update_layout(**CHART_LAYOUT, title=None)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to display daily conversation counts.")

# ═══════════════════════════════════════════════════════════════════════════════
# ROW 3 – Top Sources + Feedback Over Time
# ═══════════════════════════════════════════════════════════════════════════════
r3_left, r3_right = st.columns(2)

# ── Top Knowledge Sources ────────────────────────────────────────────────────
with r3_left:
    st.markdown("#### 📚 Top Knowledge Sources")
    top_sources = data.get("top_sources") or []
    if top_sources:
        source_names = [s.get("source_name", "Unknown") for s in top_sources]
        usage_counts = [s.get("usage_count", 0) for s in top_sources]

        # Generate a color gradient from #6C63FF → #4ECDC4
        n = len(source_names)
        colors = [
            f"rgb({108 + int((78 - 108) * i / max(n - 1, 1))}, "
            f"{99 + int((205 - 99) * i / max(n - 1, 1))}, "
            f"{255 + int((196 - 255) * i / max(n - 1, 1))})"
            for i in range(n)
        ]

        fig = go.Figure(
            go.Bar(
                y=source_names,
                x=usage_counts,
                orientation="h",
                marker_color=colors,
            )
        )
        fig.update_layout(**CHART_LAYOUT, title=None)
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No knowledge source usage data available.")

# ── Feedback Over Time ───────────────────────────────────────────────────────
with r3_right:
    st.markdown("#### 📝 Feedback Over Time")
    feedback_data = data.get("feedback_over_time") or []
    if feedback_data:
        dates = [d.get("date", "") for d in feedback_data]
        positive = [d.get("positive_count", 0) for d in feedback_data]
        negative = [d.get("negative_count", 0) for d in feedback_data]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=dates,
                y=positive,
                name="Positive",
                marker_color="#4ECDC4",
            )
        )
        fig.add_trace(
            go.Bar(
                x=dates,
                y=negative,
                name="Negative",
                marker_color="#FF6B6B",
            )
        )
        fig.update_layout(**CHART_LAYOUT, barmode="stack", title=None)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No feedback data available yet.")
