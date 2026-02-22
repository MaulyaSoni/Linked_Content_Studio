"""
LinkedIn Post Generator - Main Streamlit Application
=====================================================
Clean, simple interface for generating LinkedIn posts with AI.
"""

import os
import sys
import streamlit as st
import time
from typing import Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Core imports
from core.generator import LinkedInGenerator
from core.models import PostRequest, ContentType, Tone, Audience, GenerationMode

# Quality chains for post improvement (lazy load to avoid import issues)
try:
    from chains.quality_chains import (
        enforce_specificity,
        score_post_quality,
        generate_hook_options,
        ground_in_context
    )
    QUALITY_CHAINS_AVAILABLE = True
except ImportError as e:
    logger = __import__('utils.logger', fromlist=['get_logger']).get_logger(__name__)
    logger.warning(f"⚠️ Quality chains unavailable: {e}")
    QUALITY_CHAINS_AVAILABLE = False
    
    # Provide no-op functions if import fails
    def enforce_specificity(post): return post
    def score_post_quality(post): return None
    def generate_hook_options(post, context="", tone="", audience=""): return None
    def ground_in_context(post, context): return post

# UI imports
from ui.components import UIComponents
from ui.styles import setup_page_config, apply_custom_css, render_loading_animation, render_inline_loader

# Agentic Studio imports (lazy — only fail at use-time if missing)
try:
    from ui.multi_modal_input import render_multi_modal_input
    from ui.agent_dashboard import render_agent_dashboard, update_agent_status, render_agentic_results
    from core.models import MultiModalInput
    AGENTIC_UI_AVAILABLE = True
except ImportError as _agentic_import_err:
    AGENTIC_UI_AVAILABLE = False

# Utils
from utils.logger import get_logger
from utils.exceptions import LinkedInGeneratorError, format_error_for_user


class LinkedInPostApp:
    """Main application class for LinkedIn post generation."""
    
    def __init__(self):
        """Initialize the application."""
        self.logger = get_logger(__name__)
        
        # Initialize generator
        try:
            self.generator = LinkedInGenerator()
            self.logger.info("✅ LinkedIn generator initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize generator: {e}")
            self.generator = None
    
    def run(self):
        """Run the main application."""
        # Setup page
        setup_page_config()
        apply_custom_css()
        
        # Initialize session state
        self._init_session_state()
        
        # Render UI
        self._render_app()
    
    def _init_session_state(self):
        """Initialize Streamlit session state."""
        if 'posts_generated' not in st.session_state:
            st.session_state.posts_generated = 0
        if 'current_response' not in st.session_state:
            st.session_state.current_response = None
        if 'generation_count' not in st.session_state:
            st.session_state.generation_count = 0
        if 'agentic_response' not in st.session_state:
            st.session_state.agentic_response = None
        if 'show_scheduler' not in st.session_state:
            st.session_state.show_scheduler = False
        if 'dark_mode' not in st.session_state:
            st.session_state.dark_mode = False
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def _render_app(self):
        """Render the main application interface."""
        # Sidebar (rendered first so toggle is available)
        UIComponents.render_sidebar()

        # Header
        UIComponents.render_header()

        # Main content
        self._render_main_content()
    
    def _render_main_content(self):
        """Render the main content generation interface."""
        
        if not self.generator:
            st.error("❌ Generator not available. Please check your configuration.")
            st.info("💡 Make sure you have GROQ_API_KEY set in your .env file")
            return
        
        # Post Type Selection (Top Level)
        post_type = st.radio(
            "📝 Select Post Type",
            [
                "🚀 SIMPLE Topic",
                "📊 ADVANCED GitHub",
                "🏆 HACKATHON Project",
                "🤖 AGENTIC Studio",
            ],
            horizontal=True,
        )
        
        st.markdown("---")

        # ── Agentic Studio ────────────────────────────────────────────────
        if post_type == "🤖 AGENTIC Studio":
            self._render_agentic_studio()
            return

        # Handle Hackathon separately
        if post_type == "🏆 HACKATHON Project":
            from ui.components import render_hackathon_section
            
            hackathon_request = render_hackathon_section()
            
            if hackathon_request:
                with st.spinner("🚀 Creating your hackathon story..."):
                    start_time = time.time()
                    
                    response = self.generator.generate_hackathon_post(hackathon_request)
                    elapsed = time.time() - start_time
                    
                    st.markdown("---")
                    
                    if response.success:
                        st.success("✅ Post generated successfully!")
                        
                        # Display the post
                        st.markdown('<h3 class="gradient-title gradient-title-sm">' 
                                    '<span class="gt-icon">📱</span> Your Post</h3>', unsafe_allow_html=True)
                        st.code(response.post, language="markdown")
                        
                        # Copy buttons
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("📋 Copy Post", use_container_width=True):
                                st.info("Post copied! (Paste in LinkedIn)")
                        
                        # Display hashtags
                        if response.hashtags:
                            st.markdown('<h3 class="gradient-title gradient-title-sm">' 
                                        '<span class="gt-icon">#️⃣</span> Suggested Hashtags</h3>', unsafe_allow_html=True)
                            st.code(response.hashtags)
                            
                            with col2:
                                if st.button("📋 Copy Hashtags", use_container_width=True):
                                    st.info("Hashtags copied!")
                        
                        # Display metrics
                        st.markdown("---")
                        st.markdown('<h3 class="gradient-title gradient-title-sm">' 
                                    '<span class="gt-icon">📊</span> Generation Metrics</h3>', unsafe_allow_html=True)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("⏱️ Time", f"{elapsed:.1f}s")
                        with col2:
                            st.metric("🏆 Achievement", response.achievement_level.upper())
                        with col3:
                            st.metric("📊 Reach", response.estimated_reach.upper())
                        with col4:
                            st.metric("✨ Mode", "HACKATHON")
                        
                        # Session state for feedback
                        st.session_state.generation_count += 1
                        
                    else:
                        st.error(f"❌ Generation failed: {response.error_message}")
            
            return  # Exit early for hackathon posts
        
        # Regular flow for SIMPLE and ADVANCED modes
        mode = GenerationMode.SIMPLE if post_type == "🚀 SIMPLE Topic" else GenerationMode.ADVANCED
        
        # Generation mode
        # mode = UIComponents.render_mode_selector()  # Commented out - now set by post_type
        
        # Content type
        content_type = UIComponents.render_content_type_selector()
        
        # Input section
        github_url, topic, text_input = UIComponents.render_input_section(mode)
        
        # Style settings
        tone, audience = UIComponents.render_style_settings()
        
        # Advanced options
        advanced_options = UIComponents.render_advanced_options()
        
        # Generate button
        if UIComponents.render_generate_button():
            self._handle_generation(
                mode=mode,
                content_type=content_type,
                github_url=github_url,
                topic=topic,
                text_input=text_input,
                tone=tone,
                audience=audience,
                advanced_options=advanced_options
            )
        
        # Display results
        if st.session_state.current_response:
            UIComponents.render_post_output(st.session_state.current_response)
    
    # ------------------------------------------------------------------
    # AGENTIC STUDIO
    # ------------------------------------------------------------------

    def _render_agentic_studio(self):
        """Render the 6-agent AI Content Studio workflow."""
        if not AGENTIC_UI_AVAILABLE:
            st.error("⚠️ Agentic UI modules failed to load. Check imports.")
            return

        if not self.generator:
            st.error("❌ Generator not available. Check your GROQ_API_KEY.")
            return

        st.markdown('<h2 class="gradient-title gradient-title-md">' 
                    '<span class="gt-icon">🤖</span> Agentic AI Content Studio</h2>', unsafe_allow_html=True)
        st.caption(
            "6 specialized AI agents analyze your content, research trends, "
            "build strategy, write 3 post variants, align your brand voice, "
            "and predict engagement — all in one pipeline."
        )

        # Multi-modal input panel
        input_data = render_multi_modal_input()

        if input_data:
            st.markdown("---")
            st.markdown('<h3 class="gradient-title gradient-title-sm">' 
                        '<span class="gt-icon">🚀</span> Starting 6-Agent Pipeline …</h3>', unsafe_allow_html=True)

            # Agent status dashboard placeholders
            placeholders = render_agent_dashboard()
            progress_bar = st.progress(0.0, text="Initializing agents …")
            status_text = st.empty()

            # Build a WorkflowStatus callback that updates the UI
            def _status_callback(ws):
                """Update progress bar and agent card in real-time."""
                try:
                    progress_bar.progress(
                        min(ws.progress / 100.0, 1.0),
                        text=f"[{ws.agent_name}] {ws.message}"
                    )
                    status_text.markdown(
                        f"**{ws.agent_name}** — `{ws.status}` — {ws.message}"
                    )
                    update_agent_status(placeholders, ws)
                except Exception:
                    pass  # Never crash the pipeline because of a UI error

            try:
                # Build MultiModalInput
                modal = MultiModalInput(
                    text=input_data.get("text", ""),
                    image_paths=input_data.get("image_paths", []),
                    document_paths=input_data.get("document_paths", []),
                    urls=input_data.get("urls", []),
                    past_posts=input_data.get("past_posts", []),
                    tone=input_data.get("tone", "professional"),
                    audience=input_data.get("audience", "professionals"),
                )

                # Run agentic pipeline
                with st.spinner("🤖 Running AI agents …"):
                    agentic_response = self.generator.generate_with_agents(
                        input_data=modal,
                        status_callback=_status_callback,
                    )

                progress_bar.progress(1.0, text="✅ Pipeline complete!")
                status_text.empty()

                st.session_state.agentic_response = agentic_response
                st.session_state.generation_count += 1

            except Exception as e:
                self.logger.error(f"Agentic pipeline error: {e}")
                st.error(f"❌ Pipeline failed: {e}")
                if st.checkbox("🔧 Show debug info", key="agentic_debug"):
                    st.exception(e)
                return

        # Render previously-generated agentic results
        if st.session_state.get("agentic_response"):
            st.markdown("---")
            render_agentic_results(
                st.session_state.agentic_response,
                generator=self.generator,
            )

            if st.button("🔄 Generate Again", key="agentic_reset"):
                st.session_state.agentic_response = None
                st.rerun()

    # ------------------------------------------------------------------

    def _handle_generation(
        self,
        mode: GenerationMode,
        content_type: ContentType,
        github_url: str,
        topic: str,
        text_input: str,
        tone: Tone,
        audience: Audience,
        advanced_options: Dict[str, Any]
    ):
        """Handle the post generation process."""
        
        # Validate inputs
        if not UIComponents.validate_inputs(github_url, topic, text_input):
            return
        
        try:
            # Create request
            request = PostRequest(
                content_type=content_type,
                mode=mode,
                topic=topic,
                github_url=github_url,
                text_input=text_input,
                tone=tone,
                audience=audience,
                include_hashtags=advanced_options.get("include_hashtags", True),
                include_caption=advanced_options.get("include_caption", False),
                max_length=advanced_options.get("max_length", 2000)
            )
            
            # Show progress
            with st.spinner("🎯 Generating your LinkedIn post..."):
                start_time = time.time()
                
                # Generate post
                response = self.generator.generate(request)
                
                # Apply quality improvements if enabled
                if response.success and QUALITY_CHAINS_AVAILABLE:
                    has_context = bool(response.context_sources)
                    
                    # Enforce specificity if enabled
                    if advanced_options.get("enforce_specificity", True):
                        try:
                            with st.spinner("🔍 Enforcing specificity..."):
                                improved_post = enforce_specificity(response.post)
                                if improved_post and improved_post != response.post:
                                    response.post = improved_post
                                    self.logger.info("✅ Specificity enforcement applied")
                        except Exception as e:
                            self.logger.error(f"⚠️ Specificity enforcement failed: {e}")
                    
                    # Ground claims in context if enabled and context available
                    if advanced_options.get("ground_claims", True) and has_context:
                        try:
                            with st.spinner("✓ Verifying claims against context..."):
                                grounded_post = ground_in_context(response.post, "\n".join(response.context_sources))
                                if grounded_post and grounded_post != response.post:
                                    response.post = grounded_post
                                    self.logger.info("✅ Context grounding applied")
                        except Exception as e:
                            self.logger.error(f"⚠️ Context grounding failed: {e}")
                    
                    # Generate hook options if enabled and simple mode
                    if advanced_options.get("generate_hook_options", False) and mode == GenerationMode.SIMPLE:
                        try:
                            with st.spinner("🎣 Generating hook options..."):
                                hook_options = generate_hook_options(response.post)
                                if hook_options:
                                    response.hook_options = hook_options
                                    self.logger.info("✅ Hook options generated")
                        except Exception as e:
                            self.logger.error(f"⚠️ Hook generation failed: {e}")
                    
                    # Score post quality if enabled
                    if advanced_options.get("show_quality_score", True):
                        try:
                            with st.spinner("📊 Scoring post quality..."):
                                quality_score = score_post_quality(response.post)
                                if quality_score:
                                    response.quality_score = quality_score
                                    self.logger.info("✅ Quality score calculated")
                        except Exception as e:
                            self.logger.error(f"⚠️ Quality scoring failed: {e}")
                
                # Update session state
                st.session_state.current_response = response
                st.session_state.posts_generated += 1
                st.session_state.generation_count += 1

                # Track in chat history
                import datetime as _dt
                st.session_state.chat_history.append({
                    "topic": topic or github_url or text_input[:40] or "Post",
                    "mode": mode.value,
                    "time": _dt.datetime.now().strftime("%H:%M"),
                })
                
                # Log generation
                self.logger.log_generation_success(
                    mode.value,
                    time.time() - start_time,
                    response.tokens_used
                )
            
            # Show success message
            if response.success:
                st.success(f"✅ Post generated in {response.generation_time:.1f} seconds!")
            else:
                st.error(f"❌ Generation failed: {response.error_message}")
        
        except LinkedInGeneratorError as e:
            self.logger.error(f"Generation error: {e}")
            st.error(format_error_for_user(e))
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            st.error("❌ Something went wrong. Please try again.")
            
            # Show debug info in development
            if st.checkbox("🔧 Show debug info"):
                st.exception(e)


def main():
    """Main entry point."""
    try:
        app = LinkedInPostApp()
        app.run()
    
    except Exception as e:
        st.error(f"❌ Application failed to start: {str(e)}")
        st.info("💡 Please check your configuration and try again.")
        
        # Show debug info
        if st.checkbox("🔧 Show debug info"):
            st.exception(e)


if __name__ == "__main__":
    main()
