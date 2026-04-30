"""
UI Components - Reusable Streamlit Components
=============================================
Clean, reusable UI components for the LinkedIn post generator.
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
from core.models import (
    ContentType, Tone, Audience, GenerationMode,
    get_content_types, get_tones, get_audiences
)


class UIComponents:
    """Collection of reusable UI components."""
    
    @staticmethod
    def render_header():
        """Render application header."""
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #0077B5; margin-bottom: 0.5rem;">
                💼 LinkedIn Post Generator
            </h1>
            <p style="color: #666; font-size: 1.1rem;">
                Transform ideas into engaging LinkedIn posts with AI
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_mode_selector() -> GenerationMode:
        """Render generation mode selector."""
        st.markdown("### 🎯 Generation Mode")
        
        # Initialize mode in session state if not present
        if 'generation_mode' not in st.session_state:
            st.session_state.generation_mode = GenerationMode.SIMPLE
        
        col1, col2 = st.columns(2)
        
        with col1:
            simple_selected = st.button(
                "⚡ Simple Mode",
                use_container_width=True,
                help="Fast generation (1-3s) using direct LLM prompting"
            )
        
        with col2:
            advanced_selected = st.button(
                "🚀 Advanced Mode", 
                use_container_width=True,
                help="Enhanced generation (8-15s) with RAG context"
            )
        
        # Update mode in session state when a button is clicked
        if advanced_selected:
            st.session_state.generation_mode = GenerationMode.ADVANCED
        elif simple_selected:
            st.session_state.generation_mode = GenerationMode.SIMPLE
        
        # Get mode from session state
        mode = st.session_state.generation_mode
        
        # Show mode info
        if mode == GenerationMode.ADVANCED:
            st.info("🚀 **Advanced Mode**: Uses repository analysis for higher quality posts")
        else:
            st.info("⚡ **Simple Mode**: Fast generation that works with any input")
        
        return mode
    
    @staticmethod
    def render_content_type_selector() -> ContentType:
        """Render content type selector."""
        st.markdown("### 📝 Content Type")
        
        content_types = get_content_types()
        selected_display = st.selectbox(
            "Choose your content style:",
            options=list(content_types.values()),
            index=0,
            help="Different content types use specialized prompts"
        )
        
        # Convert back to enum
        for enum_val, display_name in content_types.items():
            if display_name == selected_display:
                return ContentType(enum_val)
        
        return ContentType.EDUCATIONAL
    
    @staticmethod
    def render_input_section(mode: GenerationMode) -> Tuple[str, str, str]:
        """Render input section based on mode."""
        st.markdown("### 📊 Content Input")
        
        github_url = ""
        topic = ""
        text_input = ""
        
        if mode == GenerationMode.ADVANCED:
            # Initialize input method in session state if not present
            if 'input_method' not in st.session_state:
                st.session_state.input_method = "📂 GitHub Repository"
            
            # Advanced mode supports all input types
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
                    placeholder="Paste your content here...",
                    height=150,
                    help="Any text content to transform into a LinkedIn post",
                    key="text_input_area"
                )
        else:
            # Simple mode - topic focused
            topic = st.text_input(
                "Topic:",
                placeholder="e.g., The future of AI, productivity tips, etc.",
                help="What topic do you want to write about?",
                key="topic_input_simple"
            )
        
        return github_url, topic, text_input
    
    @staticmethod
    def render_style_settings() -> Tuple[Tone, Audience]:
        """Render tone and audience settings."""
        st.markdown("### 🎨 Style Settings")
        
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
            
            # Convert back to enum
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
                index=2,  # Default to "Professionals"
                label_visibility="collapsed"
            )
            
            # Convert back to enum
            audience = Audience.PROFESSIONALS
            for enum_val, display_name in audiences.items():
                if display_name == selected_audience_display:
                    audience = Audience(enum_val)
                    break
        
        return tone, audience
    
    @staticmethod
    def render_advanced_options() -> Dict[str, any]:
        """Render advanced generation options."""
        with st.expander("🔧 Advanced Options", expanded=False):
            
            # Basic generation options
            col1, col2 = st.columns(2)
            
            with col1:
                include_hashtags = st.checkbox("Include Hashtags", value=True)
                include_caption = st.checkbox("Include Caption", value=False)
            
            with col2:
                max_length = st.slider("Max Length", 500, 3000, 2000, 100)
            
            # Quality improvement options
            st.markdown("---")
            st.markdown("### 🎯 Quality Improvements")
            
            col3, col4 = st.columns(2)
            
            with col3:
                enforce_specificity_flag = st.checkbox(
                    "🎯 Enforce Specificity",
                    value=True,
                    help="Remove vague phrases and tie metrics to root causes"
                )
                show_quality_score = st.checkbox(
                    "📊 Show Quality Score",
                    value=True,
                    help="Display quality metrics (clarity, specificity, engagement, credibility, actionability)"
                )
            
            with col4:
                generate_hook_options_flag = st.checkbox(
                    "🎣 Generate Hook Options",
                    value=False,
                    help="Generate 3 hook options (curiosity, outcome, contrarian) for better engagement"
                )
                ground_claims = st.checkbox(
                    "✓ Verify Claims",
                    value=True,
                    help="Ground claims in context to prevent hallucination of metrics"
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
    
    @staticmethod
    def render_generate_button() -> bool:
        """Render the main generation button."""
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            generate_clicked = st.button(
                "🚀 Generate LinkedIn Post",
                use_container_width=True,
                type="primary"
            )
        
        return generate_clicked
    
    @staticmethod
    def render_post_output(response):
        """Render generated post with copy functionality."""
        if not response.success:
            st.error(f"❌ Generation failed: {response.error_message}")
            return
        
        st.markdown("## 📋 Generated Post")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Time", f"{response.generation_time:.1f}s")
        with col2:
            st.metric("Mode", response.mode_used.title())
        with col3:
            st.metric("Quality", response.hook_strength.title())
        
        # Quality Score Section
        if hasattr(response, 'quality_score') and response.quality_score:
            st.markdown("---")
            st.markdown("### 📊 Quality Analysis")
            
            score_data = response.quality_score
            
            # Display individual scores
            if isinstance(score_data, dict):
                col1, col2, col3 = st.columns(3)
                
                metrics = list(score_data.items())
                for idx, (metric, value) in enumerate(metrics[:3]):
                    with [col1, col2, col3][idx]:
                        # Convert value to float and create a color indicator
                        try:
                            numeric_value = float(str(value).split('/')[0]) if '/' in str(value) else float(value)
                            color = "🟢" if numeric_value >= 7 else "🟡" if numeric_value >= 5 else "🔴"
                            st.metric(metric.replace('_', ' ').title(), f"{color} {value}")
                        except:
                            st.metric(metric.replace('_', ' ').title(), value)
                
                # Display remaining scores if any
                if len(metrics) > 3:
                    col1, col2 = st.columns(2)
                    for idx, (metric, value) in enumerate(metrics[3:]):
                        with [col1, col2][idx % 2]:
                            try:
                                numeric_value = float(str(value).split('/')[0]) if '/' in str(value) else float(value)
                                color = "🟢" if numeric_value >= 7 else "🟡" if numeric_value >= 5 else "🔴"
                                st.metric(metric.replace('_', ' ').title(), f"{color} {value}")
                            except:
                                st.metric(metric.replace('_', ' ').title(), value)
        
        # Hook Options Section
        if hasattr(response, 'hook_options') and response.hook_options:
            st.markdown("---")
            st.markdown("### 🎣 Hook Options")
            
            hook_data = response.hook_options
            if isinstance(hook_data, dict):
                selected_hook = st.radio(
                    "Select a hook to use:",
                    options=list(hook_data.keys()),
                    format_func=lambda x: f"**{x.title()}** - {hook_data[x][:60]}..."
                )
                
                if selected_hook:
                    st.info(f"✨ **{selected_hook.title()} Hook:**\n\n{hook_data[selected_hook]}")
        
        # Post content
        full_post = response.post
        if response.hashtags:
            full_post += f"\n\n{response.hashtags}"
        
        st.markdown("### ✏️ Your Post (Editable)")
        edited_post = st.text_area(
            "Edit your post:",
            value=full_post,
            height=300
        )
        
        # Copy buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Copy Full Post", use_container_width=True):
                st.success("✅ Ready to paste on LinkedIn!")
                st.code(edited_post, language="text")
        
        with col2:
            if st.button("📄 Copy Post Only", use_container_width=True):
                st.success("✅ Post text copied!")
                st.code(response.post, language="text")
        
        with col3:
            if st.button("#️⃣ Copy Hashtags", use_container_width=True):
                st.success("✅ Hashtags copied!")
                st.code(response.hashtags, language="text")
        
        # Context info
        if response.context_sources:
            with st.expander("📊 Sources Used"):
                for source in response.context_sources:
                    st.write(f"• {source}")
    
    @staticmethod
    def render_sidebar():
        """Render sidebar with information."""
        with st.sidebar:
            st.markdown("## 💡 LinkedIn Tips")
            
            tips = [
                "🎯 Hook readers in the first line",
                "📱 Use short paragraphs for mobile",
                "🤝 End with questions for engagement",
                "📊 Include specific data or examples",
                "🔥 Share thoughtful contrarian views"
            ]
            
            for tip in tips:
                st.write(tip)
            
            st.markdown("---")
            st.markdown("## 🔧 System Status")
            
            # Check system health (would connect to actual generator)
            st.success("✅ LLM Provider: Ready")
            
            # Show current mode from session state
            current_mode = st.session_state.get('generation_mode', GenerationMode.SIMPLE)
            mode_display = "Advanced" if current_mode == GenerationMode.ADVANCED else "Simple"
            st.info(f"ℹ️ Mode: {mode_display}")
    
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


# ============================================================================
# HACKATHON SECTION - Standalone Function
# ============================================================================

def render_hackathon_section():
    """Render hackathon/competition input section"""
    
    from core.models import HackathonProjectRequest, HackathonAchievement, HackathonType
    
    st.markdown("## 🏆 Hackathon & Competition Post")
    st.markdown("Create an engaging post about your hackathon/competition experience")
    
    # Basic Information
    col1, col2 = st.columns(2)
    
    with col1:
        hackathon_name = st.text_input(
            "Hackathon/Competition Name *",
            placeholder="e.g., Odoo X Adani Hackathon, HackUVA 2024",
            help="The official name of the hackathon or competition"
        )
        
        project_name = st.text_input(
            "Your Project Name *",
            placeholder="e.g., WaterFlow, GreenRoute",
            help="The name of your solution/project"
        )
    
    with col2:
        team_size = st.slider(
            "Team Size",
            min_value=1,
            max_value=10,
            value=4,
            help="How many people were on your team?"
        )
        
        completion_time = st.selectbox(
            "Time Spent",
            ["24 hours", "36 hours", "48 hours", "72 hours"],
            help="How long was the hackathon?"
        )
    
    # Achievement Level
    col1, col2 = st.columns(2)
    
    with col1:
        achievement = st.selectbox(
            "Achievement Level",
            ["Participant", "Top 10", "Top 5", "Runner-up", "Winner", "Special Mention"],
            help="What was your final achievement?"
        )
    
    with col2:
        hackathon_type = st.selectbox(
            "Hackathon Type",
            ["General", "AI/ML", "Web Development", "Mobile", "Sustainability", "Healthcare", "FinTech"],
            help="What was the focus of this hackathon?"
        )
    
    # Problem Statement
    st.markdown("### 📋 Problem & Solution")
    
    problem = st.text_area(
        "What problem does your project solve? *",
        placeholder="e.g., City water management faces challenges like aging infrastructure, inefficient supply chains, and lack of real-time monitoring affecting millions worldwide.",
        height=100,
        help="Be specific about the real-world problem"
    )
    
    solution = st.text_area(
        "How does your solution work? *",
        placeholder="e.g., We built an ML model integrated with MERN stack that detects anomalies in water usage patterns and enables proactive maintenance.",
        height=100,
        help="Explain your technical approach"
    )
    
    # Tech Stack & Features
    st.markdown("### 💻 Tech Stack & Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tech_input = st.text_input(
            "Technologies Used (comma-separated)",
            placeholder="React, Node.js, MongoDB, Python, ML, Google Maps API",
            help="List all major tech used in your project"
        )
        tech_stack = [t.strip() for t in tech_input.split(",") if t.strip()]
    
    with col2:
        team_members_input = st.text_input(
            "Team Member Names (comma-separated, optional)",
            placeholder="Alice, Bob, Charlie",
            help="Names of your team members to credit them"
        )
        team_members = [m.strip() for m in team_members_input.split(",") if m.strip()]
    
    features_input = st.text_area(
        "Key Features (one per line)",
        placeholder="Real-time anomaly detection\nPattern recognition using ML\nProactive maintenance alerts\nInteractive dashboard",
        height=80,
        help="Main features of your solution"
    )
    key_features = [f.strip() for f in features_input.split("\n") if f.strip()]
    
    # Personal Journey & Learnings
    st.markdown("### 🌟 Your Journey & Learnings")
    
    personal_journey = st.text_area(
        "Your Personal Journey *",
        placeholder="e.g., Finally, after all these years of learning, building, and dreaming… I participated in my first hackathon!",
        height=80,
        help="The emotional/personal aspect of your journey"
    )
    
    learnings_input = st.text_area(
        "Key Learnings (one per line)",
        placeholder="Data-driven decision making with ML is crucial\nGreat teams move fast with clear communication\nConstraints spark innovation and creativity",
        height=100,
        help="Important lessons from this experience"
    )
    key_learnings = [l.strip() for l in learnings_input.split("\n") if l.strip()]
    
    # Tone and Audience
    col1, col2 = st.columns(2)
    
    with col1:
        tone = st.selectbox(
            "Tone",
            ["Thoughtful", "Enthusiastic", "Bold", "Casual"],
            help="How should the post feel?"
        )
    
    with col2:
        audience = st.selectbox(
            "Target Audience",
            ["Developers", "Founders", "Professionals", "General Tech Community"],
            help="Who should this post resonate with?"
        )
    
    # Create request object
    if st.button("✨ Generate Hackathon Post", type="primary", use_container_width=True):
        
        # Validate required fields
        if not hackathon_name or not project_name or not problem or not solution:
            st.error("❌ Please fill in all required fields (marked with *)")
            return None
        
        if not personal_journey:
            st.error("❌ Please share your personal journey - it makes the post more authentic!")
            return None
        
        try:
            # Map string values to enums
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
