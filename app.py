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

# UI imports
from ui.components import UIComponents
from ui.styles import setup_page_config, apply_custom_css

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
    
    def _render_app(self):
        """Render the main application interface."""
        # Header
        UIComponents.render_header()
        
        # Main layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            self._render_main_content()
        
        with col2:
            UIComponents.render_sidebar()
    
    def _render_main_content(self):
        """Render the main content generation interface."""
        
        if not self.generator:
            st.error("❌ Generator not available. Please check your configuration.")
            st.info("💡 Make sure you have GROQ_API_KEY set in your .env file")
            return
        
        # Generation mode
        mode = UIComponents.render_mode_selector()
        
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
                
                # Update session state
                st.session_state.current_response = response
                st.session_state.posts_generated += 1
                st.session_state.generation_count += 1
                
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
