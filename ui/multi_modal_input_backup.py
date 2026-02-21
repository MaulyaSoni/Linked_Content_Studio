"""
Multi-Modal Input Component
===========================
Streamlit UI for accepting text, images, documents, and URLs.
"""

import streamlit as st
from typing import Dict, List, Optional
from pathlib import Path
import tempfile, os


def render_multi_modal_input() -> Optional[Dict]:
    """
    Render the multi-modal input panel.
    Returns a dict with input data, or None if nothing submitted.
    """
    st.markdown("### 🎯 What would you like to post about?")
    st.markdown("*Add any combination of text, images, documents, or links.*")

    # ---- TEXT ----
    text = st.text_area(
        "📝 Topic / Text / Idea",
        placeholder=(
            "Enter your topic, paste text, describe your idea...\n"
            "e.g. 'I just shipped a RAG-powered chatbot in 48 hours'"
        ),
        height=120,
        key="agentic_text_input",
    )

    col1, col2 = st.columns(2)

    # ---- IMAGES ----
    with col1:
        st.markdown("**🖼️ Images (optional)**")
        uploaded_images = st.file_uploader(
            "Drop images here",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="agentic_images",
            label_visibility="collapsed",
        )

    # ---- DOCUMENTS ----
    with col2:
        st.markdown("**📄 Documents (optional)**")
        uploaded_docs = st.file_uploader(
            "Drop documents here",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            key="agentic_docs",
            label_visibility="collapsed",
        )

    # ---- URLs ----
    st.markdown("**🔗 URLs / Links (optional)**")
    url_input = st.text_input(
        "Paste URLs separated by commas or spaces",
        placeholder="https://example.com, https://another.com",
        key="agentic_urls",
        label_visibility="collapsed",
    )

    # ---- BRAND POSTS ----
    with st.expander("🧬 Brand DNA (optional — paste 3-10 of your past posts)", expanded=False):
        st.markdown(
            "Paste 3-10 of your past LinkedIn posts. "
            "The AI will learn your voice and keep all variants on-brand."
        )
        past_posts_raw = st.text_area(
            "Past posts (separate with '---')",
            height=150,
            key="agentic_past_posts",
            label_visibility="collapsed",
        )

    # ---- STYLE ----
    st.markdown("---")
    col_t, col_a = st.columns(2)
    with col_t:
        tone = st.selectbox(
            "🎨 Preferred Tone",
            ["professional", "casual", "enthusiastic", "thoughtful", "bold"],
            key="agentic_tone",
        )
    with col_a:
        audience = st.selectbox(
            "👥 Target Audience",
            ["professionals", "developers", "founders", "entrepreneurs", "tech_leaders", "general"],
            key="agentic_audience",
        )

    # ---- SUBMIT ----
    st.markdown("---")
    if not st.button("🚀 Generate with AI Agents", type="primary", use_container_width=True, key="agentic_submit"):
        return None

    # Validate
    urls = [u.strip() for u in url_input.replace(",", " ").split() if u.strip().startswith("http")]
    has_input = bool(text.strip() or uploaded_images or uploaded_docs or urls)
    if not has_input:
        st.error("❌ Please provide at least one input: text, image, document, or URL.")
        return None

    # Save uploaded files to temp directory
    image_paths = _save_uploads(uploaded_images, "img")
    doc_paths = _save_uploads(uploaded_docs, "doc")
    past_posts = [p.strip() for p in past_posts_raw.split("---") if p.strip()] if past_posts_raw else []

    return {
        "text": text.strip(),
        "image_paths": image_paths,
        "document_paths": doc_paths,
        "urls": urls,
        "past_posts": past_posts,
        "tone": tone,
        "audience": audience,
    }


def _save_uploads(files, prefix: str) -> List[str]:
    """Save Streamlit uploaded files to temp directory, return paths."""
    if not files:
        return []
    paths = []
    tmp_dir = Path(tempfile.gettempdir()) / "agentic_studio"
    tmp_dir.mkdir(exist_ok=True)
    for f in files:
        dest = tmp_dir / f"{prefix}_{f.name}"
        dest.write_bytes(f.read())
        paths.append(str(dest))
    return paths
