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
            
            col1, col2 = st.columns(2)
            
            with col1:
                include_hashtags = st.checkbox("Include Hashtags", value=True)
                include_caption = st.checkbox("Include Caption", value=False)
            
            with col2:
                max_length = st.slider("Max Length", 500, 3000, 2000, 100)
        
        return {
            "include_hashtags": include_hashtags,
            "include_caption": include_caption,
            "max_length": max_length
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
