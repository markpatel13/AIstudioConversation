"""Governance & Audit Trail – review conversations, manage approvals, track compliance."""

import streamlit as st

st.set_page_config(page_title="Governance", page_icon="🛡️", layout="wide")

import pandas as pd

from components.styles import CUSTOM_CSS, render_sidebar, score_bar_html
from utils.api_client import get_client

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    render_sidebar()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-title">Governance &amp; Audit Trail</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="page-subtitle">Review conversations, manage approvals, and track compliance</p>',
    unsafe_allow_html=True,
)

client = get_client()

# ── Filter bar ───────────────────────────────────────────────────────────────
f1, f2, _ = st.columns([1, 1, 2])

with f1:
    risk_filter = st.selectbox(
        "Hallucination Risk",
        options=["All", "⚠️ Risky Only", "✅ Safe Only"],
        key="gov_risk_filter",
    )
with f2:
    status_filter = st.selectbox(
        "Reviewer Status",
        options=["All", "pending", "approved", "flagged"],
        key="gov_status_filter",
    )

# Map UI selections to API params
hallucination_risk_param = None
if risk_filter == "⚠️ Risky Only":
    hallucination_risk_param = True
elif risk_filter == "✅ Safe Only":
    hallucination_risk_param = False

status_param = None if status_filter == "All" else status_filter

# ── Fetch data ───────────────────────────────────────────────────────────────
audit_data = client.get_audit_trail(
    hallucination_risk=hallucination_risk_param,
    reviewer_status=status_param,
)

if not audit_data:
    st.info(
        "No audit records found. Click **🌱 Seed Demo Data** in the sidebar to "
        "populate sample conversations."
    )
else:
    # ── Summary dataframe ────────────────────────────────────────────────────
    st.subheader("📊 Quick Overview")

    summary_rows = []
    for record in audit_data:
        conv_id = record.get("id", "—")
        prompt = record.get("prompt", "")
        prompt_short = (prompt[:50] + "…") if len(prompt) > 50 else prompt
        risk = record.get("hallucination_risk", False)
        relevance = record.get("relevance_score", 0)
        groundedness = record.get("groundedness_score", 0)
        status = record.get("reviewer_status", "pending")
        reviewer = record.get("reviewer_name", "—")

        risk_label = "⚠️ Risk" if risk else "✅ Safe"
        status_label = {"pending": "🟡 Pending", "approved": "✅ Approved", "flagged": "🚩 Flagged"}.get(
            status, status
        )

        summary_rows.append(
            {
                "ID": conv_id,
                "Prompt": prompt_short,
                "Hallucination": risk_label,
                "Relevance": f"{relevance:.0%}",
                "Groundedness": f"{groundedness:.0%}",
                "Status": status_label,
                "Reviewer": reviewer,
            }
        )

    df = pd.DataFrame(summary_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Detailed expandable rows ─────────────────────────────────────────────
    st.divider()
    st.subheader("🔍 Detailed Review")

    for idx, record in enumerate(audit_data):
        conv_id = record.get("id", idx)
        prompt = record.get("prompt", "N/A")
        response = record.get("response", "N/A")
        relevance = record.get("relevance_score", 0)
        groundedness = record.get("groundedness_score", 0)
        risk = record.get("hallucination_risk", False)
        status = record.get("reviewer_status", "pending")
        reviewer = record.get("reviewer_name", "—")

        # Badges
        risk_badge = (
            '<span class="badge-risk">⚠️ Hallucination Risk</span>'
            if risk
            else '<span class="badge-safe">✅ Safe</span>'
        )
        status_badge_class = {
            "pending": "badge-pending",
            "approved": "badge-approved",
            "flagged": "badge-flagged",
        }.get(status, "badge-pending")
        status_badge = f'<span class="{status_badge_class}">{status.title()}</span>'

        header_label = f"Conversation #{conv_id}"
        with st.expander(header_label, expanded=False):
            st.markdown(
                f"{risk_badge} &nbsp; {status_badge}",
                unsafe_allow_html=True,
            )

            st.markdown("---")

            st.markdown("**Prompt:**")
            st.code(prompt, language=None)

            st.markdown("**Response:**")
            st.code(response, language=None)

            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(
                    score_bar_html("Relevance", relevance), unsafe_allow_html=True
                )
            with sc2:
                st.markdown(
                    score_bar_html("Groundedness", groundedness),
                    unsafe_allow_html=True,
                )

            st.caption(f"Reviewer: **{reviewer}**")

            # ── Action buttons ───────────────────────────────────────────────
            btn_col1, btn_col2, _ = st.columns([1, 1, 3])
            with btn_col1:
                if st.button(
                    "✅ Approve",
                    key=f"approve_{conv_id}_{idx}",
                    use_container_width=True,
                ):
                    client.update_review(conv_id, reviewer_status="approved")
                    st.success("Approved!")
                    st.rerun()
            with btn_col2:
                if st.button(
                    "🚩 Flag",
                    key=f"flag_{conv_id}_{idx}",
                    use_container_width=True,
                ):
                    client.update_review(conv_id, reviewer_status="flagged")
                    st.warning("Flagged!")
                    st.rerun()
