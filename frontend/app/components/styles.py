"""Shared CSS styles for the AI Conversation Studio frontend."""

CUSTOM_CSS = """
<style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global reset ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Main area background ── */
    .stApp {
        background-color: #0f1117;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #161b27 !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    [data-testid="stSidebar"] * {
        font-size: 0.88rem;
    }

    .sidebar-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.3px;
        margin-bottom: 2px;
    }

    .sidebar-subtitle {
        color: #6b7280;
        font-size: 0.78rem;
        margin-top: 0;
        margin-bottom: 16px;
    }

    .sidebar-section-label {
        color: #6b7280;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 18px 0 6px 0;
    }

    /* ── Status badges ── */
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        margin: 6px 0 10px 0;
    }

    .status-live {
        background: rgba(34, 197, 94, 0.12);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.25);
    }

    .status-mock {
        background: rgba(250, 204, 21, 0.10);
        color: #facc15;
        border: 1px solid rgba(250, 204, 21, 0.22);
    }

    /* ── Page titles ── */
    h1.page-title {
        font-size: 2rem;
        font-weight: 700;
        color: #f9fafb;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
        margin-top: 0;
    }

    .page-subtitle {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 28px;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #4b5563;
    }

    .empty-state-icon {
        font-size: 2rem;
        margin-bottom: 14px;
        color: #374151;
    }

    .empty-state-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #6b7280;
        margin: 0 0 8px 0;
    }

    .empty-state-sub {
        font-size: 0.85rem;
        color: #4b5563;
        max-width: 420px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── Chat bubbles ── */
    .chat-user {
        background: #1d4ed8;
        color: #fff;
        padding: 12px 18px;
        border-radius: 16px 16px 4px 16px;
        margin: 8px 0 8px 18%;
        font-size: 0.92rem;
        line-height: 1.55;
        box-shadow: 0 2px 10px rgba(29, 78, 216, 0.25);
        animation: fadeSlideRight 0.25s ease;
    }

    .chat-assistant {
        background: #1e2235;
        border: 1px solid rgba(255,255,255,0.07);
        color: #e5e7eb;
        padding: 12px 18px;
        border-radius: 16px 16px 16px 4px;
        margin: 8px 18% 8px 0;
        font-size: 0.92rem;
        line-height: 1.55;
        animation: fadeSlideLeft 0.25s ease;
    }

    .chat-meta {
        color: #374151;
        font-size: 0.72rem;
        margin-top: 4px;
        margin-bottom: 6px;
    }

    /* ── Score badges ── */
    .badge-safe {
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.2);
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-risk {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.2);
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-pending {
        background: rgba(250, 204, 21, 0.1);
        color: #facc15;
        border: 1px solid rgba(250, 204, 21, 0.2);
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-approved {
        background: rgba(34, 197, 94, 0.1);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.2);
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-flagged {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.2);
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    /* ── Knowledge cards ── */
    .knowledge-card {
        background: #1a1f2e;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
        transition: border-color 0.2s ease;
    }

    .knowledge-card:hover {
        border-color: rgba(99, 102, 241, 0.35);
    }

    .knowledge-card-header {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: 8px;
    }

    .knowledge-card-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f3f4f6;
    }

    .knowledge-card-meta {
        font-size: 0.72rem;
        color: #6b7280;
    }

    .knowledge-card-preview {
        color: #9ca3af;
        font-size: 0.83rem;
        line-height: 1.55;
        margin: 0;
    }

    .tag {
        background: rgba(99, 102, 241, 0.12);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.2);
        padding: 2px 9px;
        border-radius: 10px;
        font-size: 0.72rem;
        font-weight: 500;
        display: inline-block;
        margin: 2px 4px 2px 0;
    }

    /* ── Upload info box ── */
    .upload-info {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 8px;
        padding: 14px 16px;
        font-size: 0.82rem;
        color: #6b7280;
        line-height: 1.7;
        margin-top: 12px;
    }

    /* ── Form section label ── */
    .form-section-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 10px;
    }

    /* ── Score bars ── */
    .score-bar-container {
        background: rgba(255,255,255,0.06);
        border-radius: 6px;
        height: 6px;
        margin: 4px 0 10px 0;
        overflow: hidden;
    }

    .score-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }

    .score-bar-good  { background: linear-gradient(90deg, #22c55e, #16a34a); }
    .score-bar-medium{ background: linear-gradient(90deg, #facc15, #eab308); }
    .score-bar-bad   { background: linear-gradient(90deg, #ef4444, #dc2626); }

    /* ── Metric cards ── */
    .metric-card {
        background: #1a1f2e;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 18px 22px;
        transition: border-color 0.2s ease;
    }

    .metric-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
    }

    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #f9fafb;
        margin: 4px 0;
    }

    .metric-label {
        color: #6b7280;
        font-size: 0.78rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-icon { font-size: 1.2rem; margin-bottom: 4px; }

    /* ── Animations ── */
    @keyframes fadeSlideLeft {
        from { opacity: 0; transform: translateX(-12px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    @keyframes fadeSlideRight {
        from { opacity: 0; transform: translateX(12px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .fade-in { animation: fadeIn 0.3s ease; }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.18s ease;
        border: 1px solid rgba(255,255,255,0.08);
        background: #1e2235;
        color: #d1d5db;
    }

    .stButton > button:hover {
        border-color: rgba(99, 102, 241, 0.4);
        background: rgba(99, 102, 241, 0.1);
        color: #a5b4fc;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 0.85rem;
        font-weight: 500;
        padding: 8px 16px;
        color: #6b7280;
        border-radius: 6px 6px 0 0;
    }

    .stTabs [aria-selected="true"] {
        color: #a5b4fc !important;
        background: rgba(99, 102, 241, 0.08) !important;
        border-bottom: 2px solid #6366f1 !important;
    }

    /* ── Data table ── */
    .dataframe { border: none !important; }
</style>
"""


def score_color(score: float) -> str:
    """Return CSS class suffix based on a 0-1 score."""
    if score >= 0.7:
        return "good"
    elif score >= 0.4:
        return "medium"
    return "bad"


def score_bar_html(label: str, score: float) -> str:
    """Return HTML for a labeled score progress bar."""
    pct = int(score * 100)
    color = score_color(score)
    return f"""
    <div style="margin-bottom: 2px;">
        <span style="color: #9ca3af; font-size: 0.78rem;">{label}: <strong style="color: #f9fafb;">{pct}%</strong></span>
    </div>
    <div class="score-bar-container">
        <div class="score-bar-fill score-bar-{color}" style="width: {pct}%;"></div>
    </div>
    """


def render_sidebar():
    """Render the common sidebar header and navigation controls."""
    import streamlit as st
    from utils.api_client import get_client

    st.markdown('<p class="sidebar-header">AI Conversation Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-subtitle">Governance &amp; Observability</p>', unsafe_allow_html=True)
    st.divider()

    client = get_client()

    if st.button("Seed Demo Data", use_container_width=True, help="Populate the database with sample data"):
        with st.spinner("Seeding…"):
            result = client.seed_database()
            if result:
                st.success(f"Seeded {result.get('conversations', 0)} conversations!")
                st.rerun()

    st.divider()
