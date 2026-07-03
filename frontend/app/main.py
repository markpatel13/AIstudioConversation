"""
AI Conversation Studio – Conversation Playground
=================================================
Main page: interactive chat backed by Groq API (falls back to mock LLM),
real-time evaluation scores, and human feedback.
"""

import uuid
import os
import streamlit as st

st.set_page_config(
    page_title="AI Conversation Studio",
    page_icon="assets/icon.png" if os.path.exists("assets/icon.png") else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.styles import CUSTOM_CSS, score_bar_html, render_sidebar
from utils.api_client import get_client

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

client = get_client()

# ── Session State ──────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

# ── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    render_sidebar()

    st.markdown('<p class="sidebar-section-label">Knowledge Source</p>', unsafe_allow_html=True)
    sources = client.list_knowledge_sources()
    source_options = {s["name"]: s["id"] for s in sources}
    selected_source = st.selectbox(
        "Knowledge Source",
        options=["None  (Direct Chat)"] + list(source_options.keys()),
        help="Ground responses to a knowledge source, or chat freely with Groq.",
        label_visibility="collapsed",
    )
    source_id = source_options.get(selected_source)

    if selected_source == "None  (Direct Chat)":
        groq_key_set = bool(os.getenv("GROQ_API_KEY", ""))
        if groq_key_set:
            st.markdown(
                '<div class="status-badge status-live">Groq API · Active</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-badge status-mock">Mock LLM · No Key</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<p class="sidebar-section-label">Session</p>', unsafe_allow_html=True)
    st.text_input(
        "Session ID",
        value=st.session_state.session_id,
        key="session_id_input",
        help="Group conversations by session",
        label_visibility="collapsed",
    )

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.rerun()

    st.divider()

    # Session stats
    total_msgs = len(st.session_state.messages)
    eval_count = 0
    avg_rel = 0.0
    for msg in st.session_state.messages:
        if msg.get("evaluation"):
            avg_rel += msg["evaluation"].get("relevance_score", 0)
            eval_count += 1
    if eval_count > 0:
        avg_rel /= eval_count

    st.markdown('<p class="sidebar-section-label">Session Stats</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric("Messages", total_msgs)
    col2.metric("Avg Relevance", f"{avg_rel:.0%}")

# ── Main Content ────────────────────────────────────────────────────────────

st.markdown(
    '<h1 class="page-title">Conversation Playground</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="page-subtitle">Chat with the AI assistant, view evaluation scores, and provide feedback</p>',
    unsafe_allow_html=True,
)

# ── Chat History ────────────────────────────────────────────────────────────

chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">&#9679;</div>
                <p class="empty-state-title">Start a conversation</p>
                <p class="empty-state-sub">Type a message below. Select a knowledge source from the sidebar to ground responses, or chat freely.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-assistant">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

            # Evaluation scores
            evaluation = msg.get("evaluation")
            if evaluation:
                with st.expander("Evaluation Scores", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(
                            score_bar_html("Relevance", evaluation.get("relevance_score", 0)),
                            unsafe_allow_html=True,
                        )
                    with c2:
                        st.markdown(
                            score_bar_html("Groundedness", evaluation.get("groundedness_score", 0)),
                            unsafe_allow_html=True,
                        )
                    with c3:
                        st.markdown(
                            score_bar_html("Coherence", evaluation.get("coherence_score", 0)),
                            unsafe_allow_html=True,
                        )
                    if evaluation.get("hallucination_risk"):
                        st.markdown(
                            '<span class="badge-risk">Hallucination Risk</span>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<span class="badge-safe">Grounded Response</span>',
                            unsafe_allow_html=True,
                        )

            # Meta info
            meta_parts = []
            if msg.get("latency_ms"):
                meta_parts.append(f"{msg['latency_ms']:.0f} ms")
            if msg.get("model_name"):
                meta_parts.append(msg["model_name"])
            if meta_parts:
                st.markdown(
                    f'<div class="chat-meta">{" · ".join(meta_parts)}</div>',
                    unsafe_allow_html=True,
                )

            # Feedback buttons
            conv_id = msg.get("conversation_id")
            if conv_id:
                fb_cols = st.columns([1, 1, 8])
                with fb_cols[0]:
                    if st.button("Helpful", key=f"up_{i}_{conv_id}", help="Mark as helpful"):
                        client.submit_feedback(conv_id, thumbs_up=True)
                        st.toast("Positive feedback recorded!")
                with fb_cols[1]:
                    if st.button("Not helpful", key=f"down_{i}_{conv_id}", help="Mark as not helpful"):
                        client.submit_feedback(conv_id, thumbs_up=False)
                        st.toast("Negative feedback recorded.")

# ── Chat Input ──────────────────────────────────────────────────────────────

if prompt := st.chat_input("Ask anything…"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Generating response…"):
        result = client.send_message(
            prompt=prompt,
            session_id=st.session_state.session_id,
            source_id=source_id,
        )

    if result:
        st.session_state.messages.append({
            "role": "assistant",
            "content": result.get("response", ""),
            "evaluation": result.get("evaluation"),
            "latency_ms": result.get("latency_ms"),
            "model_name": result.get("model_name"),
            "conversation_id": result.get("id"),
        })
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Sorry, I could not generate a response. Please check the backend connection.",
        })

    st.rerun()
