"""
Agent Dashboard — Premium UI
=============================
Streamlit UI for visualizing the 6-agent workflow in real-time
with bold borders, gradient cards, mode-coloured presentation,
and LinkedIn publishing options.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from agents.agent_orchestrator import WorkflowStatus
from ui.styles import _get_theme, get_mode_color, render_section_header


# ─────────────────────────────────────────────────────────────────────────
# WORKFLOW VISUALIZER
# ─────────────────────────────────────────────────────────────────────────

AGENT_INFO = {
    "InputProcessor":      ("📥", "Input Processor",     "Analyzing your content"),
    "Research":            ("🔬", "Research Agent",       "Gathering market intelligence"),
    "ContentIntelligence": ("🧠", "Content Intelligence", "Building content strategy"),
    "Generation":          ("✍️",  "Generation Agent",    "Writing 3 post variants"),
    "BrandVoice":          ("🎨", "Brand Voice",          "Personalizing to your brand"),
    "Optimization":        ("⚡", "Optimization",         "Predicting engagement & timing"),
}


def render_agent_dashboard():
    """Renders an empty agent status dashboard with premium cards."""
    T = _get_theme()
    st.markdown('<h3 class="gradient-title gradient-title-md"><span class="gt-icon">🤖</span> AI Agent Workflow</h3>',
                unsafe_allow_html=True)
    placeholders = {}
    cols = st.columns(3)
    agent_list = list(AGENT_INFO.items())

    for i, (key, (icon, label, desc)) in enumerate(agent_list):
        col = cols[i % 3]
        with col:
            ph = col.empty()
            ph.markdown(_agent_card(icon, label, desc, "waiting"), unsafe_allow_html=True)
            placeholders[key] = ph

    return placeholders


def update_agent_status(placeholders: Dict, status: WorkflowStatus):
    """Update one agent's card based on a WorkflowStatus event."""
    key = status.agent_name
    if key not in placeholders or key not in AGENT_INFO:
        return
    icon, label, desc = AGENT_INFO[key]
    display_msg = status.message or desc
    placeholders[key].markdown(
        _agent_card(icon, label, display_msg, status.status),
        unsafe_allow_html=True,
    )


def _agent_card(icon: str, label: str, message: str, status: str) -> str:
    """Build a themed agent-status card."""
    T = _get_theme()
    # Status-dependent styling
    styles = {
        "waiting": {
            "bg": T.BG_SECONDARY, "border": T.SURFACE_BORDER,
            "text": T.TEXT_MUTED, "badge": "⏳", "badge_bg": T.SURFACE_BORDER
        },
        "running": {
            "bg": T.SURFACE, "border": T.PRIMARY,
            "text": T.TEXT, "badge": "🔄", "badge_bg": T.PRIMARY
        },
        "complete": {
            "bg": T.SURFACE, "border": T.SUCCESS,
            "text": T.TEXT, "badge": "✅", "badge_bg": T.SUCCESS
        },
        "error": {
            "bg": T.SURFACE, "border": T.ERROR,
            "text": T.TEXT, "badge": "❌", "badge_bg": T.ERROR
        },
        "skipped": {
            "bg": T.BG_SECONDARY, "border": T.SURFACE_BORDER,
            "text": T.TEXT_MUTED, "badge": "⏭️", "badge_bg": T.SURFACE_BORDER
        },
    }
    s = styles.get(status, styles["waiting"])

    # Pulse animation for running state
    pulse = ""
    if status == "running":
        pulse = (
            "animation: agentPulse 1.5s ease-in-out infinite;"
        )

    return f"""
    <style>
    @keyframes agentPulse {{
        0%,100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }}
        50%     {{ box-shadow: 0 0 16px 4px {s['border']}40; }}
    }}
    </style>
    <div style="
        background: {s['bg']};
        border: 2px solid {s['border']};
        border-radius: 14px;
        padding: 14px 16px;
        margin: 6px 0;
        {pulse}
        transition: all 0.3s ease;
    ">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <b style="color:{s['text']};font-family:'Plus Jakarta Sans',sans-serif;font-size:0.95rem;">
                {icon} {label}
            </b>
            <span style="font-size:1.1rem;">{s['badge']}</span>
        </div>
        <div style="color:{T.TEXT_MUTED};font-family:'Poppins',sans-serif;
                    font-size:0.8rem;margin-top:4px;">
            {message[:80]}
        </div>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────
# RESULTS DISPLAY
# ─────────────────────────────────────────────────────────────────────────

def render_agentic_results(response, generator=None):
    """Render the full agentic results panel with premium styling."""
    T = _get_theme()

    if not response or not response.success:
        st.error(f"❌ {response.error_message if response else 'Generation failed'}")
        return

    st.success(f"✅ Done in {response.total_time:.1f}s — {len(response.agents_run)} agents ran")

    # ── 3 VARIANT TABS ──
    st.markdown('<h3 class="gradient-title gradient-title-md" style="margin-top:1.5rem;">'
                '<span class="gt-icon">📱</span> Your 3 Post Variants</h3>', unsafe_allow_html=True)

    best = response.best_variant
    variant_meta = {
        "storyteller":  ("📖", "Storyteller",  T.PRIMARY),
        "strategist":   ("📊", "Strategist",   T.ACCENT_CYAN),
        "provocateur":  ("🔥", "Provocateur",  T.ACCENT_RED),
    }

    tabs = st.tabs([
        f"{variant_meta[k][0]} {variant_meta[k][1]} {'⭐' if k == best else ''}"
        for k in ["storyteller", "strategist", "provocateur"]
    ])

    for tab, variant_key in zip(tabs, ["storyteller", "strategist", "provocateur"]):
        with tab:
            post_text = response.variants.get(variant_key, "")
            if not post_text:
                st.info("Variant not generated.")
                continue

            v_icon, v_name, v_color = variant_meta[variant_key]

            # ── Post presentation card — classic B&W with mode-accent ──
            st.markdown(f"""
            <div style="background:{T.SURFACE};border:2px solid {T.SURFACE_BORDER};
                        border-radius:16px;padding:1.5rem;margin:0.5rem 0;
                        border-left:5px solid {v_color};">
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                            font-size:1rem;color:{v_color};margin-bottom:0.75rem;">
                    {v_icon} {v_name} Variant {'⭐ Best Pick' if variant_key == best else ''}
                </div>
                <pre style="white-space:pre-wrap;word-wrap:break-word;
                            font-family:'Poppins',sans-serif;font-size:0.92rem;
                            line-height:1.6;color:{T.TEXT};
                            background:transparent;border:none;padding:0;margin:0;">
{post_text}
                </pre>
            </div>
            """, unsafe_allow_html=True)

            # ── Action buttons with bold colour combos ──
            bc = st.columns(4)
            with bc[0]:
                if st.button(f"📋 Copy", key=f"copy_{variant_key}", use_container_width=True):
                    st.code(post_text, language="text")
                    st.toast("Copied! Paste into LinkedIn.")
            with bc[1]:
                st.download_button(
                    "⬇️ Download",
                    data=post_text,
                    file_name=f"linkedin_{variant_key}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key=f"dl_{variant_key}"
                )
            with bc[2]:
                if st.button(f"📤 Post Now", key=f"post_{variant_key}", use_container_width=True, type="primary"):
                    if generator:
                        with st.spinner("📤 Posting to LinkedIn…"):
                            from tools.linkedin_poster import LinkedInPoster
                            poster = LinkedInPoster()
                            result = poster.post_to_linkedin(
                                post_content=post_text,
                                hashtags=response.hashtags,
                            )
                        if result.success:
                            st.success(f"✅ Posted! [View Post]({result.post_url})")
                        else:
                            st.error(f"❌ {result.error_message}")
                    else:
                        st.info("Generator not available.")
            with bc[3]:
                if st.button(f"⏰ Schedule", key=f"sched_{variant_key}", use_container_width=True):
                    st.session_state[f"sched_show_{variant_key}"] = True

            # ── Inline scheduler ──
            if st.session_state.get(f"sched_show_{variant_key}"):
                sc1, sc2 = st.columns(2)
                with sc1:
                    sched_date = st.date_input("Date", value=datetime.now().date() + timedelta(days=1),
                                               key=f"sched_date_{variant_key}")
                with sc2:
                    sched_time = st.time_input("Time", key=f"sched_time_{variant_key}")
                if st.button("✅ Confirm Schedule", key=f"confirm_{variant_key}"):
                    iso = datetime.combine(sched_date, sched_time).isoformat()
                    if generator:
                        from tools.linkedin_poster import LinkedInPoster
                        poster = LinkedInPoster()
                        result = poster.schedule_post(
                            post_content=post_text,
                            scheduled_time=iso,
                            hashtags=response.hashtags,
                        )
                        if result.success:
                            st.success(f"✅ Scheduled for {iso}!")
                        else:
                            st.error(f"❌ {result.error_message}")
                    st.session_state[f"sched_show_{variant_key}"] = False

            # ── Engagement metrics ──
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

    # ── HASHTAGS ──
    if response.hashtags:
        st.markdown("---")
        st.markdown('<h3 class="gradient-title gradient-title-sm"><span class="gt-icon">#️⃣</span> Hashtags</h3>',
                    unsafe_allow_html=True)
        st.code(response.hashtags)
        if st.button("📋 Copy Hashtags", key="copy_hashtags"):
            st.toast("Hashtags copied!")

    # ── STRATEGY ──
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

    # ── RECOMMENDATIONS ──
    if response.overall_recommendations:
        with st.expander("💡 Optimization Recommendations", expanded=True):
            for rec in response.overall_recommendations:
                st.markdown(f"- {rec}")


def _render_linkedin_publishing(response, generator):
    """Legacy wrapper — kept for backward compatibility."""
    # Publishing is now inline in each variant tab above.
    pass
