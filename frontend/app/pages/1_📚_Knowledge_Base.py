"""Knowledge Base Manager – upload and manage knowledge sources."""

import streamlit as st

st.set_page_config(page_title="Knowledge Base", layout="wide")

from components.styles import CUSTOM_CSS, render_sidebar
from utils.api_client import get_client

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    render_sidebar()

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-title">Knowledge Base</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="page-subtitle">Manage knowledge sources that ground your AI assistant\'s responses</p>',
    unsafe_allow_html=True,
)

client = get_client()

# ── Tab layout ─────────────────────────────────────────────────────────────
tab_sources, tab_add = st.tabs(["Existing Sources", "Add New Source"])

# ── Tab: Existing sources ──────────────────────────────────────────────────
with tab_sources:
    sources = client.list_knowledge_sources()

    if not sources:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">&#9679;</div>
                <p class="empty-state-title">No knowledge sources yet</p>
                <p class="empty-state-sub">Switch to the "Add New Source" tab to create your first source.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for idx, source in enumerate(sources):
            source_id = source.get("id", idx)
            name = source.get("name", "Untitled")
            content = source.get("content", "")
            preview = content[:250]
            tags_raw = source.get("tags", "")
            created = source.get("created_at", "N/A")

            tag_html = ""
            if tags_raw:
                tag_list = [t.strip() for t in tags_raw.split(",") if t.strip()]
                tag_html = " ".join(
                    f'<span class="tag">{t}</span>' for t in tag_list
                )

            char_count = len(content)

            card_html = f"""
            <div class="knowledge-card">
                <div class="knowledge-card-header">
                    <span class="knowledge-card-name">{name}</span>
                    <span class="knowledge-card-meta">{char_count:,} chars &nbsp;·&nbsp; {created[:10] if created != 'N/A' else 'N/A'}</span>
                </div>
                <p class="knowledge-card-preview">{preview}{'…' if len(content) > 250 else ''}</p>
                <div style="margin-top: 10px;">{tag_html}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            if st.button(
                "Delete",
                key=f"del_knowledge_{source_id}_{idx}",
                help=f"Delete '{name}'",
            ):
                if client.delete_knowledge_source(source_id):
                    st.success(f"Deleted **{name}**")
                    st.rerun()

# ── Tab: Add new source ────────────────────────────────────────────────────
with tab_add:
    left_col, right_col = st.columns([1, 1], gap="large")

    # ── Manual text entry ─────────────────────────────────────────────
    with left_col:
        st.markdown('<p class="form-section-label">Paste Text</p>', unsafe_allow_html=True)
        with st.form("add_knowledge_form", clear_on_submit=True):
            source_name = st.text_input(
                "Name",
                placeholder="e.g. Company FAQ",
            )
            source_content = st.text_area(
                "Content",
                height=220,
                placeholder="Paste your knowledge content here…",
            )
            source_tags = st.text_input(
                "Tags",
                placeholder="faq, support, onboarding  (comma-separated)",
            )
            submitted = st.form_submit_button("Create Source", use_container_width=True)

        if submitted:
            if not source_name or not source_content:
                st.warning("Please provide both a name and content.")
            else:
                result = client.create_knowledge_source(
                    name=source_name,
                    content=source_content,
                    tags=source_tags if source_tags else None,
                )
                if result:
                    st.success(f"Created source **{source_name}**")
                    st.rerun()

    # ── File upload ───────────────────────────────────────────────────
    with right_col:
        st.markdown('<p class="form-section-label">Upload File</p>', unsafe_allow_html=True)

        with st.form("upload_knowledge_form", clear_on_submit=True):
            upload_name = st.text_input(
                "Source Name",
                placeholder="e.g. Product Manual",
            )
            upload_tags = st.text_input(
                "Tags",
                placeholder="manual, product, v2  (comma-separated)",
            )
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["txt", "md", "pdf", "docx", "csv"],
                help="Supported formats: TXT, Markdown, PDF, DOCX, CSV",
            )
            upload_submitted = st.form_submit_button("Upload & Create", use_container_width=True)

        if upload_submitted:
            if not uploaded_file:
                st.warning("Please select a file to upload.")
            else:
                _name = upload_name or uploaded_file.name
                with st.spinner("Uploading and extracting text…"):
                    result = client.upload_knowledge_file(
                        name=_name,
                        file_bytes=uploaded_file.getvalue(),
                        filename=uploaded_file.name,
                        tags=upload_tags or "",
                    )
                if result:
                    st.success(f"Uploaded **{_name}** successfully!")
                    st.rerun()

        st.markdown(
            """
            <div class="upload-info">
                <strong>Supported formats</strong><br>
                TXT &nbsp;·&nbsp; Markdown &nbsp;·&nbsp; PDF &nbsp;·&nbsp; DOCX &nbsp;·&nbsp; CSV<br><br>
                Text is extracted and stored so the AI can use it as context.
            </div>
            """,
            unsafe_allow_html=True,
        )
