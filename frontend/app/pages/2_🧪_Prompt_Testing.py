"""Prompt Testing Lab – create templates, run test suites, compare outputs."""

import streamlit as st

st.set_page_config(page_title="Prompt Testing", page_icon="🧪", layout="wide")

from components.styles import CUSTOM_CSS, render_sidebar, score_bar_html
from utils.api_client import get_client

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    render_sidebar()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-title">Prompt Testing Lab</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="page-subtitle">Create prompt templates, run test suites, and compare outputs side-by-side</p>',
    unsafe_allow_html=True,
)

client = get_client()
templates = client.list_prompt_templates()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_create, tab_run = st.tabs(["Create Template", "Run Tests"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Create Template
# ═══════════════════════════════════════════════════════════════════════════════
with tab_create:
    with st.form("create_template_form", clear_on_submit=True):
        tmpl_name = st.text_input("Template Name", placeholder="e.g. Customer Support v2")
        tmpl_text = st.text_area(
            "Template Text",
            height=200,
            placeholder="Write your prompt here. Use {input} as a placeholder for test inputs.",
            help="Use **{input}** where you want each test input to be substituted.",
        )
        tmpl_inputs = st.text_area(
            "Test Inputs (one per line)",
            height=120,
            placeholder="What is your return policy?\nHow do I reset my password?",
        )
        submitted = st.form_submit_button("💾 Save Template", use_container_width=True)

    if submitted:
        if not tmpl_name or not tmpl_text:
            st.warning("Please provide both a name and template text.")
        else:
            test_inputs_list = [
                line.strip()
                for line in tmpl_inputs.strip().splitlines()
                if line.strip()
            ] if tmpl_inputs else None
            result = client.create_prompt_template(
                name=tmpl_name,
                template_text=tmpl_text,
                test_inputs=test_inputs_list,
            )
            if result:
                st.success(f"✅ Template **{tmpl_name}** created!")
                st.rerun()

    # ── Existing templates ───────────────────────────────────────────────────
    st.divider()
    st.subheader("📋 Existing Templates")

    if not templates:
        st.info("No templates yet. Create your first one above!")
    else:
        for idx, tmpl in enumerate(templates):
            tmpl_id = tmpl.get("id", idx)
            col_info, col_action = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{tmpl.get('name', 'Untitled')}**")
                st.caption(tmpl.get("template_text", "")[:120] + "…")
            with col_action:
                if st.button("🗑️", key=f"del_tmpl_{tmpl_id}_{idx}", help="Delete template"):
                    if client.delete_prompt_template(tmpl_id):
                        st.success("Deleted!")
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – Run Tests
# ═══════════════════════════════════════════════════════════════════════════════
with tab_run:
    if not templates:
        st.info("Create a template first in the **Create Template** tab.")
    else:
        # ── Select template ──────────────────────────────────────────────────
        template_names = {t.get("name", f"Template {t.get('id')}"): t for t in templates}
        selected_name = st.selectbox(
            "Select Template", options=list(template_names.keys())
        )
        selected_tmpl = template_names[selected_name]
        tmpl_id = selected_tmpl.get("id")

        # Pre-populate test inputs from saved template
        saved_inputs = selected_tmpl.get("test_inputs") or []
        default_inputs = "\n".join(saved_inputs) if saved_inputs else ""

        test_input_text = st.text_area(
            "Test Inputs (one per line)",
            value=default_inputs,
            height=120,
            key="run_test_inputs",
        )

        if st.button("🚀 Run Test Suite", use_container_width=True, type="primary"):
            inputs_list = [
                line.strip()
                for line in test_input_text.strip().splitlines()
                if line.strip()
            ] if test_input_text else []

            if not inputs_list:
                st.warning("Please provide at least one test input.")
            else:
                with st.spinner("Running test suite…"):
                    results = client.run_prompt_test(
                        template_id=tmpl_id, test_inputs=inputs_list
                    )

                if not results:
                    st.error("No results returned. Check your backend connection.")
                else:
                    st.success(f"✅ Completed {len(results)} test(s)")
                    st.divider()

                    for r_idx, result in enumerate(results):
                        test_input = result.get("input", "")
                        output = result.get("output", "")
                        relevance = result.get("relevance_score", 0)
                        groundedness = result.get("groundedness_score", 0)
                        hallucination = result.get("hallucination_risk", False)
                        latency = result.get("latency_ms", 0)

                        # Color helpers
                        def _score_color_hex(s: float) -> str:
                            if s >= 0.7:
                                return "#4ECDC4"
                            elif s >= 0.4:
                                return "#FFD166"
                            return "#FF6B6B"

                        risk_badge = (
                            '<span class="badge-risk">⚠️ High Risk</span>'
                            if hallucination
                            else '<span class="badge-safe">✅ Safe</span>'
                        )

                        st.markdown(f"##### Test #{r_idx + 1}")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**Input:**")
                            st.code(test_input, language=None)
                        with c2:
                            st.markdown("**Output:**")
                            st.code(output, language=None)

                        sc1, sc2, sc3, sc4 = st.columns(4)
                        with sc1:
                            st.markdown(
                                score_bar_html("Relevance", relevance),
                                unsafe_allow_html=True,
                            )
                        with sc2:
                            st.markdown(
                                score_bar_html("Groundedness", groundedness),
                                unsafe_allow_html=True,
                            )
                        with sc3:
                            st.markdown(
                                f"**Hallucination:** {risk_badge}",
                                unsafe_allow_html=True,
                            )
                        with sc4:
                            st.metric("Latency", f"{latency} ms")

                        st.divider()
