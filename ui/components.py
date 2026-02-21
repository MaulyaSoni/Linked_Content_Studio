"""
UI Components - Premium Reusable Streamlit Components
=====================================================
Bold, modern components with gradient headings, Jakarta Sans / Poppins fonts,
working post-action buttons, and polished cards & borders.
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
from core.models import (
    ContentType, Tone, Audience, GenerationMode,
    get_content_types, get_tones, get_audiences
)
from ui.styles import _get_theme, get_mode_color, render_section_header


# ═══════════════════════════════════════════════════════════════════════════
# MAIN UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════

class UIComponents:
    """Collection of reusable UI components with premium styling."""

    # ── HEADER ────────────────────────────────────────────────────────────

    @staticmethod
    def render_header():
        """Render the application header with shiny gradient title."""
        T = _get_theme()
        st.markdown(f"""
        <div class="fade-in" style="text-align:center;padding:2rem 0 1.5rem 0;">
            <div style="font-size:3rem;margin-bottom:0.3rem;">💼</div>
            <h1 class="gradient-title gradient-title-lg" style="margin:0;">
                LinkedIn Post Generator
            </h1>
            <p style="font-family:'Poppins',sans-serif;color:{T.TEXT_MUTED};
                      font-size:1.05rem;margin-top:0.4rem;">
                Transform ideas into engaging LinkedIn posts with AI
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── MODE SELECTOR ─────────────────────────────────────────────────────

    @staticmethod
    def render_mode_selector() -> GenerationMode:
        """Render generation mode selector with premium cards."""
        T = _get_theme()
        render_section_header("Generation Mode", "🎯")

        if 'generation_mode' not in st.session_state:
            st.session_state.generation_mode = GenerationMode.SIMPLE

        col1, col2 = st.columns(2)

        with col1:
            simple_active = st.session_state.generation_mode == GenerationMode.SIMPLE
            st.markdown(f"""
            <div class="mode-card {'active' if simple_active else ''}" style="min-height:110px;">
                <div style="font-size:2rem;">⚡</div>
                <div class="mode-card-title">Simple Mode</div>
                <div class="mode-card-desc">Fast generation (1-3s) — direct LLM prompting</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Simple", key="sel_simple", use_container_width=True):
                st.session_state.generation_mode = GenerationMode.SIMPLE
                st.rerun()

        with col2:
            adv_active = st.session_state.generation_mode == GenerationMode.ADVANCED
            st.markdown(f"""
            <div class="mode-card {'active' if adv_active else ''}" style="min-height:110px;">
                <div style="font-size:2rem;">🚀</div>
                <div class="mode-card-title">Advanced Mode</div>
                <div class="mode-card-desc">Enhanced (8-15s) — RAG-powered deep analysis</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Advanced", key="sel_adv", use_container_width=True):
                st.session_state.generation_mode = GenerationMode.ADVANCED
                st.rerun()

        mode = st.session_state.generation_mode
        if mode == GenerationMode.ADVANCED:
            st.info("🚀 **Advanced Mode** — Uses repository analysis for higher-quality posts")
        else:
            st.info("⚡ **Simple Mode** — Fast generation that works with any input")

        return mode

    # ── CONTENT TYPE ──────────────────────────────────────────────────────

    @staticmethod
    def render_content_type_selector() -> ContentType:
        """Render content type selector."""
        render_section_header("Content Type", "📝")

        content_types = get_content_types()
        selected_display = st.selectbox(
            "Choose your content style:",
            options=list(content_types.values()),
            index=0,
            help="Different content types use specialized prompts"
        )

        for enum_val, display_name in content_types.items():
            if display_name == selected_display:
                return ContentType(enum_val)

        return ContentType.EDUCATIONAL

    # ── INPUT SECTION ─────────────────────────────────────────────────────

    @staticmethod
    def render_input_section(mode: GenerationMode) -> Tuple[str, str, str]:
        """Render input section based on mode."""
        render_section_header("Content Input", "📊")

        github_url = ""
        topic = ""
        text_input = ""

        if mode == GenerationMode.ADVANCED:
            if 'input_method' not in st.session_state:
                st.session_state.input_method = "📂 GitHub Repository"

            input_method = st.radio(
                "Choose input method:",
                ["📂 GitHub Repository", "💡 Topic", "📄 Custom Text"],
                horizontal=True,
                key="input_method"
            )

            if input_method == "📂 GitHub Repository":
                github_url = st.text_input(
                    "GitHub Repository URL:",
                    placeholder="https://github.com/username/repository",
                    help="Public GitHub repository for context analysis",
                    key="github_url_input"
                )
            elif input_method == "💡 Topic":
                topic = st.text_input(
                    "Topic:",
                    placeholder="e.g., AI in software development, remote work tips",
                    help="What do you want to write about?",
                    key="topic_input_advanced"
                )
            else:
                text_input = st.text_area(
                    "Custom Text:",
                    placeholder="Paste your content here…",
                    height=150,
                    help="Any text content to transform into a LinkedIn post",
                    key="text_input_area"
                )
        else:
            topic = st.text_input(
                "Topic:",
                placeholder="e.g., The future of AI, productivity tips …",
                help="What topic do you want to write about?",
                key="topic_input_simple"
            )

        return github_url, topic, text_input

    # ── STYLE SETTINGS ────────────────────────────────────────────────────

    @staticmethod
    def render_style_settings() -> Tuple[Tone, Audience]:
        """Render tone and audience settings."""
        render_section_header("Style Settings", "🎨")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Tone:**")
            tones = get_tones()
            selected_tone_display = st.selectbox(
                "Choose tone:",
                options=list(tones.values()),
                index=0,
                label_visibility="collapsed"
            )
            tone = Tone.PROFESSIONAL
            for enum_val, display_name in tones.items():
                if display_name == selected_tone_display:
                    tone = Tone(enum_val)
                    break

        with col2:
            st.markdown("**Audience:**")
            audiences = get_audiences()
            selected_audience_display = st.selectbox(
                "Target audience:",
                options=list(audiences.values()),
                index=2,
                label_visibility="collapsed"
            )
            audience = Audience.PROFESSIONALS
            for enum_val, display_name in audiences.items():
                if display_name == selected_audience_display:
                    audience = Audience(enum_val)
                    break

        return tone, audience

    # ── ADVANCED OPTIONS ──────────────────────────────────────────────────

    @staticmethod
    def render_advanced_options() -> Dict[str, any]:
        """Render advanced generation options."""
        with st.expander("🔧 Advanced Options", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                include_hashtags = st.checkbox("Include Hashtags", value=True)
                include_caption = st.checkbox("Include Caption", value=False)
            with col2:
                max_length = st.slider("Max Length", 500, 3000, 2000, 100)

            st.markdown("---")
            render_section_header("Quality Improvements", "🎯")

            col3, col4 = st.columns(2)
            with col3:
                enforce_specificity_flag = st.checkbox(
                    "🎯 Enforce Specificity", value=True,
                    help="Remove vague phrases and tie metrics to root causes"
                )
                show_quality_score = st.checkbox(
                    "📊 Show Quality Score", value=True,
                    help="Display quality metrics"
                )
            with col4:
                generate_hook_options_flag = st.checkbox(
                    "🎣 Generate Hook Options", value=False,
                    help="Generate 3 hook options for better engagement"
                )
                ground_claims = st.checkbox(
                    "✓ Verify Claims", value=True,
                    help="Ground claims in context to prevent hallucination"
                )

        return {
            "include_hashtags": include_hashtags,
            "include_caption": include_caption,
            "max_length": max_length,
            "enforce_specificity": enforce_specificity_flag,
            "show_quality_score": show_quality_score,
            "generate_hook_options": generate_hook_options_flag,
            "ground_claims": ground_claims
        }

    # ── GENERATE BUTTON ───────────────────────────────────────────────────

    @staticmethod
    def render_generate_button() -> bool:
        """Render the main generation button."""
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            return st.button(
                "🚀 Generate LinkedIn Post",
                use_container_width=True,
                type="primary"
            )

    # ── POST OUTPUT ───────────────────────────────────────────────────────

    @staticmethod
    def render_post_output(response):
        """Render generated post with fully-working action buttons."""
        T = _get_theme()

        if not response.success:
            st.error(f"❌ Generation failed: {response.error_message}")
            return

        st.markdown(f"""
        <h2 class="gradient-title gradient-title-md slide-up" style="margin-top:1.5rem;">
            📋 Generated Post
        </h2>
        """, unsafe_allow_html=True)

        # ── Metrics row ──
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏱️ Time", f"{response.generation_time:.1f}s")
        with col2:
            st.metric("📡 Mode", response.mode_used.title())
        with col3:
            st.metric("🏆 Hook", response.hook_strength.title())

        # ── Quality Score Section ──
        if hasattr(response, 'quality_score') and response.quality_score:
            st.markdown("---")
            st.markdown(f"""
            <h3 class="gradient-title gradient-title-sm">📊 Quality Analysis</h3>
            """, unsafe_allow_html=True)

            score_data = response.quality_score
            if isinstance(score_data, dict):
                metrics = list(score_data.items())
                cols = st.columns(min(len(metrics), 3))
                for idx, (metric, value) in enumerate(metrics[:3]):
                    with cols[idx]:
                        try:
                            nv = float(str(value).split('/')[0]) if '/' in str(value) else float(value)
                            icon = "🟢" if nv >= 7 else "🟡" if nv >= 5 else "🔴"
                            st.metric(metric.replace('_', ' ').title(), f"{icon} {value}")
                        except Exception:
                            st.metric(metric.replace('_', ' ').title(), value)

                if len(metrics) > 3:
                    cols2 = st.columns(2)
                    for idx, (metric, value) in enumerate(metrics[3:]):
                        with cols2[idx % 2]:
                            try:
                                nv = float(str(value).split('/')[0]) if '/' in str(value) else float(value)
                                icon = "🟢" if nv >= 7 else "🟡" if nv >= 5 else "🔴"
                                st.metric(metric.replace('_', ' ').title(), f"{icon} {value}")
                            except Exception:
                                st.metric(metric.replace('_', ' ').title(), value)

        # ── Hook Options ──
        if hasattr(response, 'hook_options') and response.hook_options:
            st.markdown("---")
            st.markdown('<h3 class="gradient-title gradient-title-sm">🎣 Hook Options</h3>',
                        unsafe_allow_html=True)
            hook_data = response.hook_options
            if isinstance(hook_data, dict):
                selected_hook = st.radio(
                    "Select a hook to use:",
                    options=list(hook_data.keys()),
                    format_func=lambda x: f"**{x.title()}** — {hook_data[x][:60]}…"
                )
                if selected_hook:
                    st.info(f"✨ **{selected_hook.title()} Hook:**\n\n{hook_data[selected_hook]}")

        # ── Editable Post ──
        full_post = response.post
        if response.hashtags:
            full_post += f"\n\n{response.hashtags}"

        st.markdown('<h3 class="gradient-title gradient-title-sm" style="margin-top:1.5rem;">'
                    '✏️ Your Post (Editable)</h3>', unsafe_allow_html=True)
        edited_post = st.text_area(
            "Edit your post:",
            value=full_post,
            height=300,
            label_visibility="collapsed"
        )

        # ── Action Buttons (all working) ──
        st.markdown("---")
        btn_cols = st.columns(5)

        # 1 — Copy Full Post
        with btn_cols[0]:
            if st.button("📋 Copy Full", key="btn_copy_full", use_container_width=True):
                st.code(edited_post, language="text")
                st.success("✅ Ready to paste on LinkedIn!")

        # 2 — Copy Post Only (without hashtags)
        with btn_cols[1]:
            if st.button("📄 Copy Post", key="btn_copy_post", use_container_width=True):
                st.code(response.post, language="text")
                st.success("✅ Post text ready!")

        # 3 — Copy Hashtags
        with btn_cols[2]:
            if st.button("#️⃣ Hashtags", key="btn_copy_hash", use_container_width=True):
                if response.hashtags:
                    st.code(response.hashtags, language="text")
                    st.success("✅ Hashtags ready!")
                else:
                    st.warning("No hashtags generated.")

        # 4 — Download as TXT
        with btn_cols[3]:
            st.download_button(
                "⬇️ Download",
                data=edited_post,
                file_name="linkedin_post.txt",
                mime="text/plain",
                use_container_width=True,
                key="btn_download"
            )

        # 5 — Regenerate
        with btn_cols[4]:
            if st.button("🔄 Regenerate", key="btn_regen", use_container_width=True):
                st.session_state.current_response = None
                st.rerun()

        # ── Context Sources ──
        if response.context_sources:
            with st.expander("📊 Sources Used"):
                for source in response.context_sources:
                    st.write(f"• {source}")

    # ── SIDEBAR ───────────────────────────────────────────────────────────

    @staticmethod
    def render_sidebar():
        """Render sidebar with tips, status, account info & chat history."""
        T = _get_theme()

        with st.sidebar:
            # ── Theme toggle ──
            from ui.styles import render_theme_toggle
            render_theme_toggle()

            st.markdown("---")

            # ── LinkedIn Tips ──
            st.markdown(f"""
            <h3 class="gradient-title gradient-title-sm">💡 LinkedIn Tips</h3>
            """, unsafe_allow_html=True)
            tips = [
                "🎯 Hook readers in the first line",
                "📱 Use short paragraphs for mobile",
                "🤝 End with questions for engagement",
                "📊 Include specific data or examples",
                "🔥 Share thoughtful contrarian views"
            ]
            for tip in tips:
                st.markdown(f"""
                <div style="padding:6px 10px;margin:4px 0;border-radius:10px;
                            border:1px solid {T.SURFACE_BORDER};background:{T.BG_SECONDARY};
                            font-family:'Poppins',sans-serif;font-size:0.85rem;color:{T.TEXT};">
                    {tip}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # ── System Status ──
            st.markdown(f"""
            <h3 class="gradient-title gradient-title-sm">🔧 System Status</h3>
            """, unsafe_allow_html=True)
            st.success("✅ LLM Provider: Ready")
            current_mode = st.session_state.get('generation_mode', GenerationMode.SIMPLE)
            mode_display = "Advanced" if current_mode == GenerationMode.ADVANCED else "Simple"
            st.info(f"ℹ️ Mode: {mode_display}")

            st.markdown("---")

            # ── Account Info — simple classic UI ──
            st.markdown(f"""
            <h3 class="gradient-title gradient-title-sm">👤 Account</h3>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:{T.SURFACE};border:1px solid {T.SURFACE_BORDER};
                        border-radius:12px;padding:1rem;margin:0.5rem 0;">
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                            font-size:1rem;color:{T.TEXT};">User</div>
                <div style="font-family:'Poppins',sans-serif;font-size:0.85rem;
                            color:{T.TEXT_MUTED};margin-top:4px;">
                    Posts generated: <b>{st.session_state.get('posts_generated', 0)}</b>
                </div>
                <div style="font-family:'Poppins',sans-serif;font-size:0.85rem;
                            color:{T.TEXT_MUTED};margin-top:2px;">
                    Session count: <b>{st.session_state.get('generation_count', 0)}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # ── Chat History — simple classic UI ──
            st.markdown(f"""
            <h3 class="gradient-title gradient-title-sm">📜 Recent History</h3>
            """, unsafe_allow_html=True)

            history = st.session_state.get("chat_history", [])
            if not history:
                st.markdown(f"""
                <div style="padding:10px;border-radius:10px;background:{T.BG_SECONDARY};
                            border:1px solid {T.SURFACE_BORDER};font-family:'Poppins',sans-serif;
                            font-size:0.85rem;color:{T.TEXT_MUTED};text-align:center;">
                    No posts generated yet
                </div>
                """, unsafe_allow_html=True)
            else:
                for i, item in enumerate(history[-5:]):
                    st.markdown(f"""
                    <div style="padding:8px 10px;margin:4px 0;border-radius:10px;
                                border:1px solid {T.SURFACE_BORDER};background:{T.SURFACE};
                                font-family:'Poppins',sans-serif;font-size:0.82rem;
                                color:{T.TEXT};">
                        <b>#{i+1}</b> — {item.get('topic', 'Post')[:40]}
                        <span style="float:right;color:{T.TEXT_MUTED};font-size:0.75rem;">
                            {item.get('time', '')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

    # ── VALIDATION ────────────────────────────────────────────────────────

    @staticmethod
    def validate_inputs(github_url: str, topic: str, text_input: str) -> bool:
        """Validate user inputs."""
        if not any([github_url, topic, text_input]):
            st.error("❌ Please provide a topic, GitHub URL, or text input")
            return False
        if github_url and not github_url.startswith(('http://', 'https://')):
            st.error("❌ Please enter a valid GitHub URL")
            return False
        return True


# ═══════════════════════════════════════════════════════════════════════════
# HACKATHON SECTION
# ═══════════════════════════════════════════════════════════════════════════

def render_hackathon_section():
    """Render hackathon/competition input section with premium styling."""
    from core.models import HackathonProjectRequest, HackathonAchievement, HackathonType
    T = _get_theme()

    st.markdown(f"""
    <h2 class="gradient-title gradient-title-md slide-up">
        🏆 Hackathon & Competition Post
    </h2>
    <p style="font-family:'Poppins',sans-serif;color:{T.TEXT_MUTED};margin-bottom:1.5rem;">
        Create an engaging post about your hackathon / competition experience
    </p>
    """, unsafe_allow_html=True)

    # ── Basic Information ──
    col1, col2 = st.columns(2)
    with col1:
        hackathon_name = st.text_input(
            "Hackathon / Competition Name *",
            placeholder="e.g., Odoo X Adani Hackathon, HackUVA 2024",
            help="The official name"
        )
        project_name = st.text_input(
            "Your Project Name *",
            placeholder="e.g., WaterFlow, GreenRoute",
            help="The name of your solution"
        )
    with col2:
        team_size = st.slider("Team Size", 1, 10, 4, help="How many people?")
        completion_time = st.selectbox(
            "Time Spent",
            ["24 hours", "36 hours", "48 hours", "72 hours"]
        )

    # ── Achievement ──
    col1, col2 = st.columns(2)
    with col1:
        achievement = st.selectbox(
            "Achievement Level",
            ["Participant", "Top 10", "Top 5", "Runner-up", "Winner", "Special Mention"]
        )
    with col2:
        hackathon_type = st.selectbox(
            "Hackathon Type",
            ["General", "AI/ML", "Web Development", "Mobile", "Sustainability", "Healthcare", "FinTech"]
        )

    # ── Problem & Solution ──
    render_section_header("Problem & Solution", "📋")
    problem = st.text_area(
        "What problem does your project solve? *",
        placeholder="Be specific about the real-world problem…",
        height=100
    )
    solution = st.text_area(
        "How does your solution work? *",
        placeholder="Explain your technical approach…",
        height=100
    )

    # ── Tech Stack ──
    render_section_header("Tech Stack & Features", "💻")
    col1, col2 = st.columns(2)
    with col1:
        tech_input = st.text_input(
            "Technologies Used (comma-separated)",
            placeholder="React, Node.js, MongoDB, Python, ML"
        )
        tech_stack = [t.strip() for t in tech_input.split(",") if t.strip()]
    with col2:
        team_members_input = st.text_input(
            "Team Member Names (optional, comma-separated)",
            placeholder="Alice, Bob, Charlie"
        )
        team_members = [m.strip() for m in team_members_input.split(",") if m.strip()]

    features_input = st.text_area(
        "Key Features (one per line)",
        placeholder="Real-time anomaly detection\nPattern recognition\nInteractive dashboard",
        height=80
    )
    key_features = [f.strip() for f in features_input.split("\n") if f.strip()]

    # ── Journey & Learnings ──
    render_section_header("Your Journey & Learnings", "🌟")
    personal_journey = st.text_area(
        "Your Personal Journey *",
        placeholder="e.g., After years of learning, I finally competed in my first hackathon!",
        height=80
    )
    learnings_input = st.text_area(
        "Key Learnings (one per line)",
        placeholder="Data-driven decisions are crucial\nGreat teams communicate clearly",
        height=100
    )
    key_learnings = [l.strip() for l in learnings_input.split("\n") if l.strip()]

    # ── Tone & Audience ──
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("Tone", ["Thoughtful", "Enthusiastic", "Bold", "Casual"])
    with col2:
        audience = st.selectbox(
            "Target Audience",
            ["Developers", "Founders", "Professionals", "General Tech Community"]
        )

    # ── Submit ──
    st.markdown("---")
    if st.button("✨ Generate Hackathon Post", type="primary", use_container_width=True):
        if not hackathon_name or not project_name or not problem or not solution:
            st.error("❌ Please fill in all required fields (marked with *)")
            return None
        if not personal_journey:
            st.error("❌ Please share your personal journey!")
            return None

        try:
            achievement_map = {
                "Participant": HackathonAchievement.PARTICIPANT,
                "Top 10": HackathonAchievement.TOP_10,
                "Top 5": HackathonAchievement.TOP_5,
                "Runner-up": HackathonAchievement.RUNNER_UP,
                "Winner": HackathonAchievement.WINNER,
                "Special Mention": HackathonAchievement.SPECIAL_MENTION,
            }
            type_map = {
                "General": HackathonType.GENERAL,
                "AI/ML": HackathonType.AI_ML,
                "Web Development": HackathonType.WEB_DEV,
                "Mobile": HackathonType.MOBILE,
                "Sustainability": HackathonType.SUSTAINABILITY,
                "Healthcare": HackathonType.HEALTHCARE,
                "FinTech": HackathonType.FINTECH,
            }

            request = HackathonProjectRequest(
                hackathon_name=hackathon_name,
                project_name=project_name,
                team_size=team_size,
                team_members=team_members,
                problem_statement=problem,
                solution_description=solution,
                tech_stack=tech_stack,
                key_features=key_features,
                completion_time_hours=int(completion_time.split()[0]),
                achievement=achievement_map[achievement],
                personal_journey=personal_journey,
                key_learnings=key_learnings,
                tone=tone.lower(),
                audience=audience.lower().replace(" tech community", "").replace("general ", "general"),
                hackathon_type=type_map[hackathon_type]
            )
            return request

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return None

    return None
