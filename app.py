"""
LinkedIn Content Studio - Clean SaaS-Ready Architecture
======================================================
Transform ideas into scroll-stopping LinkedIn posts with our clean, production-ready system.

This is the main Streamlit application using our new 3-layer architecture:
- Interface Layer (UI Components)
- Core Brain Layer (Generator + Models + LLM + RAG) 
- External Loaders Layer (GitHub, Documents, Web)
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import time
from typing import Dict, Optional

# Core imports - New clean architecture
from core.generator import LinkedInGenerator
from core.models import PostRequest, PostResponse, ContentType, Tone, Audience, GenerationMode

# UI imports - Clean component system
from ui.components import (
    setup_page_config, render_header, render_mode_selector,
    render_content_type_selector, render_input_section, render_style_settings,
    render_advanced_options, render_generation_button, render_post_output,
    render_export_options, render_feedback_section, render_sidebar_stats,
    initialize_session_state
)

# Utils
import logging


class LinkedInContentApp:
    """
    Main Streamlit application class using clean architecture.
    
    This replaces the complex multi-chain system with a simple, maintainable design:
    - Single generator class handles all content creation
    - Clean UI components for better UX
    - Simple vs Advanced modes for different user needs
    """
    
    def __init__(self):
        """Initialize the clean LinkedIn Content Studio."""
        self.logger = logging.getLogger("linkedin_app")
        
        # Initialize the core generator (replaces all chains)
        try:
            self.generator = LinkedInGenerator()
            self.logger.info("LinkedInGenerator initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize LinkedInGenerator: {e}")
            st.error(f"⚠️ Initialization failed: {e}")
            self.generator = None
    
    def run(self):
        """Main application entry point."""
        
        # Setup page configuration
        setup_page_config()
        
        # Initialize session state
        initialize_session_state()
        
        # Render header
        render_header()
        
        # Create main layout
        main_col, sidebar_col = st.columns([3, 1])
        
        with main_col:
            self._render_main_interface()
        
        with sidebar_col:
            render_sidebar_stats()
    
    def _render_main_interface(self):
        """Render the main content generation interface."""
        
        if self.generator is None:
            st.error("⚠️ Generator not available. Please check your configuration.")
            return
        
        # Step 1: Mode Selection
        generation_mode = render_mode_selector()
        
        st.markdown("---")
        
        # Step 2: Content Type Selection  
        content_type = render_content_type_selector()
        
        st.markdown("---")
        
        # Step 3: Input Section
        github_url, topic, text_input = render_input_section()
        
        st.markdown("---")
        
        # Step 4: Style Settings
        tone, audience = render_style_settings()
        
        # Step 5: Advanced Options
        advanced_options = render_advanced_options()
        
        # Step 6: Generation Button
        generate_clicked = render_generation_button()
        
        # Step 7: Handle Generation
        if generate_clicked:
            self._handle_generation(
                generation_mode=generation_mode,
                content_type=content_type,
                github_url=github_url,
                topic=topic,
                text_input=text_input,
                tone=tone,
                audience=audience,
                advanced_options=advanced_options
            )
        
        # Step 8: Display Results
        if "current_post_response" in st.session_state:
            self._display_results()
    
    def _handle_generation(
        self,
        generation_mode: GenerationMode,
        content_type: ContentType, 
        github_url: str,
        topic: str,
        text_input: str,
        tone: Tone,
        audience: Audience,
        advanced_options: Dict
    ):
        """Handle the content generation process."""
        
        # Validate input
        if not any([github_url, topic, text_input]):
            st.warning("⚠️ Please provide some input content to generate a LinkedIn post.")
            return
        
        # Create post request
        post_request = PostRequest(
            content_type=content_type,
            tone=tone,
            audience=audience,
            mode=generation_mode,
            github_url=github_url if github_url else None,
            topic=topic if topic else None,
            text_input=text_input if text_input else None,
            include_hashtags=advanced_options.get("include_hashtags", True),
            include_caption=advanced_options.get("include_caption", False),
            max_length=advanced_options.get("max_length", 2000)
        )
        
        # Show generation progress
        with st.spinner("🎯 Generating your scroll-stopping LinkedIn post..."):
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Initialize
            progress_bar.progress(20)
            status_text.text("🚀 Initializing generation...")
            time.sleep(0.5)
            
            # Step 2: Generate content
            progress_bar.progress(60)
            status_text.text("✨ Creating engaging content...")
            
            try:
                post_response = self.generator.generate(post_request)
                
                # Step 3: Apply refinements if enabled
                if advanced_options.get("enable_refinement", True) and post_response.success:
                    progress_bar.progress(80)
                    status_text.text("🔧 Refining for maximum engagement...")
                    
                    refined_response = self.generator.refine_post(
                        post_response.post,
                        post_request
                    )
                    
                    if refined_response.success:
                        post_response = refined_response
                
                progress_bar.progress(100)
                status_text.text("✅ Generation complete!")
                
            except Exception as e:
                self.logger.error(f"Generation failed: {e}")
                post_response = PostResponse(
                    success=False,
                    error_message=f"Generation failed: {str(e)}"
                )
            
            finally:
                # Clear progress indicators
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
        
        # Store result in session state
        st.session_state["current_post_response"] = post_response
        
        # Update stats
        if post_response.success:
            st.session_state.posts_generated += 1
        
        # Log generation
        self.logger.info(f"Generation completed: success={post_response.success}")
    
    def _display_results(self):
        """Display the generation results with all export and feedback options."""
        
        post_response = st.session_state["current_post_response"]
        
        st.markdown("---")
        
        # Main post output with editing
        render_post_output(post_response, enable_editing=True)
        
        # Export options
        if post_response.success:
            st.markdown("---")
            render_export_options(post_response)
            
            # Feedback section
            st.markdown("---")
            render_feedback_section(post_response)
    
    def health_check(self) -> bool:
        """Check if the app is ready to generate content."""
        
        if self.generator is None:
            return False
        
        try:
            # Test LLM connectivity
            test_response = self.generator.llm_provider.test_connectivity()
            return test_response
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False


def main():
    """Main function to run the LinkedIn Content Studio."""
    
    try:
        # Initialize and run the app
        app = LinkedInContentApp()
        app.run()
        
    except Exception as e:
        st.error(f"❌ Application failed to start: {str(e)}")
        st.info("💡 Please check your environment configuration and try again.")
        
        # Show debug info in development
        if st.checkbox("🔧 Show debug info"):
            st.exception(e)


if __name__ == "__main__":
    main()