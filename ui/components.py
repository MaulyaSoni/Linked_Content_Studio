"""
UI Components - Clean Streamlit Interface
======================================
Reusable UI components for the LinkedIn content generator.
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from core.models import (
    PostRequest, ContentType, Tone, Audience, GenerationMode,
    get_content_type_display_names, get_tone_display_names, get_audience_display_names
)


class Theme:
    """Clean theme configuration."""
    
    PRIMARY_COLOR = "#0077B5"  # LinkedIn Blue
    BACKGROUND_COLOR = "#FFFFFF"
    SECONDARY_COLOR = "#F3F2EF"
    SUCCESS_COLOR = "#057642"
    WARNING_COLOR = "#B24020"
    ERROR_COLOR = "#CC1016"


def setup_page_config():
    """Configure Streamlit page with clean settings."""
    st.set_page_config(
        page_title="LinkedIn Content Studio",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/yourusername/linkedin-content-engine',
            'Report a bug': None,
            'About': "LinkedIn Content Engine - Transform ideas into engaging LinkedIn posts"
        }
    )


def render_header():
    """Render clean application header."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="color: #0077B5; margin-bottom: 0.5rem;">
            💼 LinkedIn Content Studio
        </h1>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 0;">
            Transform your ideas into scroll-stopping LinkedIn posts
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_mode_selector() -> GenerationMode:
    """Render generation mode selector with explanations."""
    
    st.markdown("### 🎯 Generation Mode")
    
    col1, col2 = st.columns(2)
    
    with col1:
        simple_selected = st.button(
            "⚡ Simple Mode", 
            use_container_width=True,
            help="Fast generation using direct prompting. Works with any input."
        )
    
    with col2:
        advanced_selected = st.button(
            "🚀 Advanced Mode",
            use_container_width=True, 
            help="Enhanced quality using repository analysis and context retrieval."
        )
    
    # Default to simple mode
    mode = GenerationMode.SIMPLE
    
    if advanced_selected:
        mode = GenerationMode.ADVANCED
        st.info("🚀 **Advanced Mode**: Uses repository analysis for higher quality, context-aware posts.")
    else:
        st.info("⚡ **Simple Mode**: Fast generation that works reliably with any input.")
    
    return mode


def render_content_type_selector() -> ContentType:
    """Render content type selector with engaging options."""
    
    st.markdown("### 📝 Content Type")
    
    content_types = get_content_type_display_names()
    
    selected_display = st.selectbox(
        "Choose your content style:",
        options=list(content_types.values()),
        index=0,
        help="Different content types use specialized prompts optimized for engagement"
    )
    
    # Convert back to enum value
    for enum_val, display_name in content_types.items():
        if display_name == selected_display:
            return ContentType(enum_val)
    
    return ContentType.EDUCATIONAL


def render_input_section() -> Tuple[str, str, str]:
    """Render input section with multiple input options."""
    
    st.markdown("### 📊 Content Input")
    
    # Input method selector
    input_method = st.radio(
        "Choose your input method:",
        ["📂 GitHub Repository", "💡 Topic/Idea", "📄 Text Content"],
        horizontal=True
    )
    
    github_url = ""
    topic = ""
    text_input = ""
    
    if input_method == "📂 GitHub Repository":
        github_url = st.text_input(
            "GitHub Repository URL:",
            placeholder="https://github.com/username/repository",
            help="Paste any public GitHub repository URL"
        )
        
        if github_url:
            st.success(f"✅ Repository: {github_url.split('/')[-1]}")
    
    elif input_method == "💡 Topic/Idea":
        topic = st.text_input(
            "What topic do you want to write about?",
            placeholder="e.g., The future of AI in software development, Remote work productivity tips, etc.",
            help="Describe the main topic or idea for your LinkedIn post"
        )
    
    else:  # Text Content
        text_input = st.text_area(
            "Paste your content:",
            placeholder="Paste article text, documentation, or any content you want to transform into a LinkedIn post...",
            height=150,
            help="Paste any text content that you want to transform into a LinkedIn post"
        )
    
    return github_url, topic, text_input


def render_style_settings() -> Tuple[Tone, Audience]:
    """Render style and audience settings."""
    
    st.markdown("### 🎨 Style Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Tone:**")
        tones = get_tone_display_names()
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
        audiences = get_audience_display_names()
        selected_audience_display = st.selectbox(
            "Target audience:",
            options=list(audiences.values()),
            index=2,  # Default to "Business Professionals"
            label_visibility="collapsed"
        )
        
        # Convert back to enum
        audience = Audience.PROFESSIONALS
        for enum_val, display_name in audiences.items():
            if display_name == selected_audience_display:
                audience = Audience(enum_val)
                break
    
    return tone, audience


def render_advanced_options() -> Dict[str, bool]:
    """Render advanced generation options."""
    
    with st.expander("🔧 Advanced Options", expanded=False):
        
        col1, col2 = st.columns(2)
        
        with col1:
            include_hashtags = st.checkbox("Include Hashtags", value=True)
            include_caption = st.checkbox("Include Video Caption", value=False)
        
        with col2:
            enable_refinement = st.checkbox("Enable Post Refinement", value=True, 
                                          help="Apply a second pass to improve engagement potential")
            max_length = st.slider("Max Post Length", 500, 3000, 2000, 100)
    
    return {
        "include_hashtags": include_hashtags,
        "include_caption": include_caption, 
        "enable_refinement": enable_refinement,
        "max_length": max_length
    }


def render_generation_button() -> bool:
    """Render the main generation button."""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        generate_clicked = st.button(
            "🚀 Generate LinkedIn Post",
            use_container_width=True,
            type="primary",
            help="Generate your scroll-stopping LinkedIn post"
        )
    
    return generate_clicked


def render_post_output(post_response, enable_editing=True):
    """Render generated post with editing capabilities."""
    
    if not post_response.success:
        st.error(f"❌ Generation failed: {post_response.error_message}")
        return
    
    st.markdown("## 📋 Your Generated LinkedIn Post")
    
    # Success metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Generation Time", f"{post_response.generation_time:.1f}s")
    with col2:
        st.metric("Mode Used", post_response.mode_used.title())
    with col3:
        st.metric("Context Sources", len(post_response.context_sources))
    with col4:
        st.metric("Estimated Quality", post_response.hook_strength.title())
    
    # Main editable post area
    st.markdown("### ✏️ Full LinkedIn Post (Editable & Ready to Copy)")
    
    # Combine post and hashtags
    full_post = post_response.post
    if post_response.hashtags:
        full_post += f"\n\n{post_response.hashtags}"
    
    if enable_editing:
        edited_post = st.text_area(
            "📝 Edit your post before sharing:",
            value=full_post,
            height=300,
            help="Click here to edit your post before copying to LinkedIn"
        )
        
        # Copy buttons  
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📋 Copy Full Post", use_container_width=True):
                st.success("✅ Ready to paste on LinkedIn!")
                st.code(edited_post, language="text")
        
        with col2:
            if st.button("📄 Copy Post Only", use_container_width=True):
                st.success("✅ Post text copied!")
                st.code(post_response.post, language="text")
        
        with col3:
            if st.button("#️⃣ Copy Hashtags", use_container_width=True):
                st.success("✅ Hashtags copied!")
                st.code(post_response.hashtags, language="text") 
        
        with col4:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.experimental_rerun()
    
    else:
        st.code(full_post, language="text")
    
    # Expandable sections for individual components
    if post_response.caption:
        with st.expander("🎥 Video Caption"):
            st.info(post_response.caption)
    
    # Context transparency
    if post_response.context_sources:
        with st.expander("📊 Content Sources"):
            st.write("**Sources used for generation:**")
            for source in post_response.context_sources:
                st.write(f"• {source.replace('_', ' ').title()}")
            
            if hasattr(post_response, 'context_quality'):
                quality_percent = int(post_response.context_quality * 100)
                st.metric("Context Quality", f"{quality_percent}%")


def render_export_options(post_response):
    """Render export functionality."""
    
    if not post_response.success:
        return
    
    st.markdown("## 📤 Export Options")
    
    st.info("""
    🎯 **Export your content in multiple formats:**
    • **Copy Ready** - Format for direct LinkedIn posting
    • **Markdown** - Save as .md file for documentation  
    • **Notion** - Import into Notion database
    • **Buffer** - Schedule with social media tools
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Convert response to dict for export handlers
    post_data = {
        "post": post_response.post,
        "hashtags": post_response.hashtags,
        "caption": post_response.caption,
        "stats": {
            "generation_time": post_response.generation_time,
            "mode_used": post_response.mode_used
        }
    }
    
    with col1:
        if st.button("📋 Copy Ready", use_container_width=True):
            try:
                from utils.export import ExportHandler
                export_text = ExportHandler.export_for_linkedin(post_data)
                st.success("✅ LinkedIn format ready!")
                st.code(export_text, language="text")
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with col2:
        if st.button("📝 Save as MD", use_container_width=True):
            try:
                from utils.export import ExportHandler
                md_content = ExportHandler.export_for_markdown(post_data, "LinkedIn Post")
                filename = f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                
                st.download_button(
                    label=f"📥 Download {filename}",
                    data=md_content,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Markdown export failed: {e}")
    
    with col3:
        if st.button("💡 Export to Notion", use_container_width=True):
            try:
                from utils.export import ExportHandler
                import json
                
                notion_data = ExportHandler.export_for_notion(post_data)
                notion_json = json.dumps(notion_data, indent=2)
                filename = f"linkedin_notion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                st.download_button(
                    label=f"📥 Download {filename}",
                    data=notion_json, 
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Notion export failed: {e}")
    
    with col4:
        if st.button("📅 Buffer Format", use_container_width=True):
            try:
                from utils.export import ExportHandler
                import json
                
                buffer_data = ExportHandler.export_for_scheduling(post_data, "buffer")
                buffer_json = json.dumps(buffer_data, indent=2)
                filename = f"linkedin_buffer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                st.download_button(
                    label=f"📥 Download {filename}",
                    data=buffer_json,
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Buffer export failed: {e}")


def render_feedback_section(post_response):
    """Render feedback collection for continuous improvement."""
    
    if not post_response.success:
        return
        
    st.markdown("## 👍 Feedback & Improvement")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    feedback_given = False
    
    with col1:
        if st.button("👍 Engaging", use_container_width=True):
            st.success("Thanks! This helps us improve.")
            feedback_given = True
    
    with col2:
        if st.button("😑 Too Generic", use_container_width=True):
            st.info("Got it. We'll make it more specific next time.")
            feedback_given = True
    
    with col3:
        if st.button("🤓 Too Technical", use_container_width=True):
            st.info("Understood. We'll make it more accessible.")
            feedback_given = True
    
    with col4:
        if st.button("🎯 Regenerate", use_container_width=True):
            st.experimental_rerun()
    
    with col5:
        if st.button("💡 Hook Ideas", use_container_width=True):
            show_hook_suggestions(post_response.post)
    
    if feedback_given:
        # Store feedback in session state for analytics
        if 'feedback_count' not in st.session_state:
            st.session_state.feedback_count = 0
        st.session_state.feedback_count += 1


def show_hook_suggestions(original_post: str):
    """Show alternative hook suggestions for the post."""
    
    st.markdown("### 🎣 Alternative Hook Ideas")
    
    hook_templates = [
        "Unpopular opinion: [first line with contrarian angle]",
        "After [X years] in [field], here's what I learned:",
        "Everyone talks about [topic], but here's what they miss:",
        "This [insight] changed how I think about [topic]:",
        "Hot take: [bold statement about the topic]"
    ]
    
    st.write("**Try these hook patterns with your content:**")
    for i, template in enumerate(hook_templates, 1):
        st.write(f"{i}. {template}")
    
    st.info("💡 **Pro tip**: The first line determines if people keep reading. Make it curiosity-driven!")


def render_sidebar_stats():
    """Render sidebar with app statistics and tips."""
    
    with st.sidebar:
        st.markdown("## 📊 App Stats")
        
        # Session stats
        if 'posts_generated' not in st.session_state:
            st.session_state.posts_generated = 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Posts Generated", st.session_state.get('posts_generated', 0))
        with col2:
            st.metric("Session Time", "0m")  # Could implement actual tracking
        
        st.markdown("---")
        
        # LinkedIn tips
        st.markdown("## 💡 LinkedIn Tips")
        
        tips = [
            "🎯 Hook your audience in the first line",
            "📱 Write for mobile - use short paragraphs", 
            "🤝 End with questions to drive engagement",
            "📊 Include data or specific examples",
            "🔥 Share contrarian but thoughtful takes", 
            "📖 Tell stories that people can relate to"
        ]
        
        for tip in tips:
            st.write(tip)
        
        st.markdown("---")
        
        # Status indicators
        st.markdown("## 🔧 System Status")
        
        # This would connect to actual system status
        st.success("✅ LLM Provider: Active")
        st.success("✅ RAG Engine: Ready") 
        st.info("ℹ️ Mode: Simple")


def initialize_session_state():
    """Initialize session state variables."""
    
    if 'posts_generated' not in st.session_state:
        st.session_state.posts_generated = 0
    
    if 'feedback_count' not in st.session_state:
        st.session_state.feedback_count = 0
    
    if 'current_post' not in st.session_state:
        st.session_state.current_post = None