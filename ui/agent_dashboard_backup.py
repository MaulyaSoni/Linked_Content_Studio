"""
Agent Dashboard
===============
Streamlit UI for visualizing the 6-agent workflow in real-time
and displaying the final results with LinkedIn publishing options.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from agents.agent_orchestrator import WorkflowStatus


# ---------------------------------------------------------------------------
# WORKFLOW VISUALIZER
# ---------------------------------------------------------------------------

AGENT_INFO = {
    "InputProcessor":     ("📥", "Input Processor",     "Analyzing your content"),
    "Research":           ("🔬", "Research Agent",       "Gathering market intelligence"),
    "ContentIntelligence":("🧠", "Content Intelligence", "Building content strategy"),
    "Generation":         ("✍️",  "Generation Agent",    "Writing 3 post variants"),
    "BrandVoice":         ("🎨", "Brand Voice",          "Personalizing to your brand"),
    "Optimization":       ("⚡", "Optimization",         "Predicting engagement & timing"),
}


def render_agent_dashboard():
    """
    Renders an empty agent status dashboard.
    Returns a dict of Streamlit placeholder objects keyed by agent name.
    """
    st.markdown("### 🤖 AI Agent Workflow")
    placeholders = {}
    cols = st.columns(3)
    agent_list = list(AGENT_INFO.items())

    for i, (key, (icon, label, desc)) in enumerate(agent_list):
        col = cols[i % 3]
        with col:
            ph = col.empty()
            ph.markdown(_agent_card(icon, label, desc, "waiting"))
            placeholders[key] = ph

    return placeholders


def update_agent_status(placeholders: Dict, status: WorkflowStatus):
    """Update one agent's card based on a WorkflowStatus event."""
    key = status.agent_name
    if key not in placeholders or key not in AGENT_INFO:
        return
    icon, label, desc = AGENT_INFO[key]
    display_msg = status.message or desc
    placeholders[key].markdown(_agent_card(icon, label, display_msg, status.status))


def _agent_card(icon: str, label: str, message: str, status: str) -> str:
    colors = {
        "waiting":  ("#f0f0f0", "#888",   "⏳"),
        "running":  ("#fff3cd", "#856404","🔄"),
        "complete": ("#d4edda", "#155724","✅"),
        "error":    ("#f8d7da", "#721c24","❌"),
        "skipped":  ("#e2e3e5", "#383d41","⏭️"),
    }
    bg, text, status_icon = colors.get(status, colors["waiting"])
    return (
        f'<div style="background:{bg};border-radius:8px;padding:12px;margin:4px 0;'
        f'border-left:4px solid {text};">'
        f'<b style="color:{text}">{icon} {label}</b> {status_icon}<br>'
        f'<small style="color:{text}">{message[:80]}</small>'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# RESULTS DISPLAY
# ---------------------------------------------------------------------------

def render_agentic_results(response, generator=None):
    """Render the full agentic results panel."""
    if not response or not response.success:
        st.error(f"❌ {response.error_message if response else 'Generation failed'}")
        return

    st.success(f"✅ Done in {response.total_time:.1f}s — {len(response.agents_run)} agents ran")

    # ---- 3 VARIANT TABS ----
    st.markdown("### 📱 Your 3 Post Variants")
    best = response.best_variant
    variant_labels = {
        "storyteller":  "📖 Storyteller",
        "strategist":   "📊 Strategist",
        "provocateur":  "🔥 Provocateur",
    }
    tabs = st.tabs([
        f"{variant_labels.get(k, k)} {'⭐' if k == best else ''}"
        for k in ["storyteller", "strategist", "provocateur"]
    ])

    for tab, variant_key in zip(tabs, ["storyteller", "strategist", "provocateur"]):
        with tab:
            post_text = response.variants.get(variant_key, "")
            if not post_text:
                st.info("Variant not generated.")
                continue

            st.code(post_text, language="markdown")

            # Copy helper (Streamlit workaround)
            col_copy, col_post, col_sched = st.columns(3)
            with col_copy:
                if st.button(f"📋 Copy", key=f"copy_{variant_key}", use_container_width=True):
                    st.toast("Copied! Paste into LinkedIn.")

            # Engagement metrics
            opt = response.optimization.get(variant_key, {})
            if opt:
                eng = opt.get("engagement", {})
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("👁️ Reach", eng.get("impressions", "—"))
                m2.metric("👍 Likes", eng.get("likes", "—"))
                m3.metric("💬 Comments", eng.get("comments", "—"))
                m4.metric("⚡ Score", f"{opt.get('virality_score', 0):.0%}")

            bf = response.brand_feedback.get(variant_key, {})
            if bf:
                score = bf.get("consistency_score", 0.7)
                st.progress(score, text=f"Brand fit: {score:.0%}")

    # ---- HASHTAGS ----
    if response.hashtags:
        st.markdown("### #️⃣ Hashtags")
        st.code(response.hashtags)
        if st.button("📋 Copy Hashtags", key="copy_hashtags"):
            st.toast("Hashtags copied!")

    # ---- STRATEGY ----
    if response.strategy:
        with st.expander("🧠 Content Strategy", expanded=False):
            s = response.strategy
            if s.get("key_message"):
                st.markdown(f"**Key Message:** {s['key_message']}")
            if s.get("target_audience"):
                st.markdown(f"**Audience:** {s['target_audience']}")
            if s.get("emotional_hook"):
                st.markdown(f"**Hook:** {s['emotional_hook']}")
            if s.get("call_to_action"):
                st.markdown(f"**CTA:** {s['call_to_action']}")

    # ---- RECOMMENDATIONS ----
    if response.overall_recommendations:
        with st.expander("💡 Optimization Recommendations", expanded=True):
            for rec in response.overall_recommendations:
                st.markdown(f"- {rec}")

    # ---- LINKEDIN PUBLISHING ----
    st.markdown("---")
    st.markdown("### 🔗 Publish to LinkedIn")
    _render_linkedin_publishing(response, generator)


def _render_linkedin_publishing(response, generator):
    """LinkedIn post/schedule UI."""
    variant_options = {
        "storyteller":  "📖 Storyteller",
        "strategist":   "📊 Strategist",
        "provocateur":  "🔥 Provocateur",
    }
    available = [k for k in variant_options if k in response.variants and response.variants[k]]
    if not available:
        st.warning("No variants available to post.")
        return

    selected_key = st.selectbox(
        "Which variant to publish?",
        available,
        format_func=lambda k: variant_options[k],
        key="publish_variant_select",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Post Now to LinkedIn", use_container_width=True, key="post_now_btn"):
            if generator:
                with st.spinner("📤 Posting to LinkedIn..."):
                    from tools.linkedin_poster import LinkedInPoster
                    poster = LinkedInPoster()
                    result = poster.post_to_linkedin(
                        post_content=response.variants[selected_key],
                        hashtags=response.hashtags,
                    )
                if result.success:
                    st.success(f"✅ Posted! [View Post]({result.post_url})")
                else:
                    st.error(f"❌ {result.error_message}")
            else:
                st.info("Generator not available.")

    with col2:
        if st.button("⏰ Schedule Post", use_container_width=True, key="schedule_btn"):
            st.session_state["show_scheduler"] = True

    if st.session_state.get("show_scheduler"):
        sched_col1, sched_col2 = st.columns(2)
        with sched_col1:
            sched_date = st.date_input("Date", value=datetime.now().date() + timedelta(days=1), key="sched_date")
        with sched_col2:
            sched_time = st.time_input("Time", key="sched_time")

        if st.button("✅ Confirm Schedule", key="confirm_schedule"):
            iso_time = datetime.combine(sched_date, sched_time).isoformat()
            if generator:
                from tools.linkedin_poster import LinkedInPoster
                poster = LinkedInPoster()
                result = poster.schedule_post(
                    post_content=response.variants[selected_key],
                    scheduled_time=iso_time,
                    hashtags=response.hashtags,
                )
                if result.success:
                    st.success(f"✅ Scheduled for {iso_time}!")
                else:
                    st.error(f"❌ {result.error_message}")
            st.session_state["show_scheduler"] = False
