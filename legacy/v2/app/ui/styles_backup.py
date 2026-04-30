"""
UI Styles - Theming and CSS
===========================
Clean styling and theming for the LinkedIn post generator.
"""

import streamlit as st


class Theme:
    """LinkedIn-inspired theme configuration."""
    
    # Colors
    PRIMARY_COLOR = "#0077B5"          # LinkedIn Blue
    SECONDARY_COLOR = "#005885"        # Darker Blue
    BACKGROUND_COLOR = "#FFFFFF"        # White
    SURFACE_COLOR = "#F3F2EF"          # Light Gray
    SUCCESS_COLOR = "#057642"          # Green
    WARNING_COLOR = "#B24020"          # Orange
    ERROR_COLOR = "#CC1016"            # Red
    
    # Typography
    FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    
    # Spacing
    SPACING_SMALL = "0.5rem"
    SPACING_MEDIUM = "1rem"
    SPACING_LARGE = "2rem"


def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app."""
    
    css = f"""
    <style>
    /* LinkedIn-inspired theme */
    .stApp {{
        font-family: {Theme.FONT_FAMILY};
    }}
    
    /* Header styling */
    .main-header {{
        text-align: center;
        padding: {Theme.SPACING_LARGE} 0;
        background: linear-gradient(135deg, {Theme.PRIMARY_COLOR}, {Theme.SECONDARY_COLOR});
        color: white;
        margin: -2rem -2rem {Theme.SPACING_MEDIUM} -2rem;
        border-radius: 0;
    }}
    
    /* Button styling */
    .stButton > button {{
        background-color: {Theme.PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {Theme.SECONDARY_COLOR};
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 119, 181, 0.2);
    }}
    
    /* Primary button styling */
    .stButton > button[kind="primary"] {{
        background-color: {Theme.PRIMARY_COLOR};
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
    }}
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {{
        border: 2px solid #E1E5E9;
        border-radius: 8px;
        padding: 0.75rem;
        transition: border-color 0.2s ease;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {{
        border-color: {Theme.PRIMARY_COLOR};
        box-shadow: 0 0 0 3px rgba(0, 119, 181, 0.1);
    }}
    
    /* Card styling */
    .card {{
        background: white;
        border: 1px solid #E1E5E9;
        border-radius: 12px;
        padding: {Theme.SPACING_LARGE};
        margin: {Theme.SPACING_MEDIUM} 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    /* Metric styling */
    .stMetric {{
        background-color: {Theme.SURFACE_COLOR};
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }}
    
    /* Success message styling */
    .stSuccess {{
        background-color: rgba(5, 118, 66, 0.1);
        border-left: 4px solid {Theme.SUCCESS_COLOR};
        padding: 1rem;
        border-radius: 4px;
    }}
    
    /* Error message styling */
    .stError {{
        background-color: rgba(204, 16, 22, 0.1);
        border-left: 4px solid {Theme.ERROR_COLOR};
        padding: 1rem;
        border-radius: 4px;
    }}
    
    /* Warning message styling */
    .stWarning {{
        background-color: rgba(178, 64, 32, 0.1);
        border-left: 4px solid {Theme.WARNING_COLOR};
        padding: 1rem;
        border-radius: 4px;
    }}
    
    /* Info message styling */
    .stInfo {{
        background-color: rgba(0, 119, 181, 0.1);
        border-left: 4px solid {Theme.PRIMARY_COLOR};
        padding: 1rem;
        border-radius: 4px;
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background-color: {Theme.SURFACE_COLOR};
        border-radius: 8px;
        font-weight: 600;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background-color: {Theme.SURFACE_COLOR};
    }}
    
    /* Code block styling */
    .stCode {{
        background-color: #F6F8FA;
        border: 1px solid #E1E5E9;
        border-radius: 6px;
        padding: 1rem;
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .main-header {{
            margin: -1rem -1rem {Theme.SPACING_MEDIUM} -1rem;
            padding: {Theme.SPACING_LARGE} {Theme.SPACING_MEDIUM};
        }}
        
        .stButton > button {{
            padding: 0.75rem 1rem;
            font-size: 0.9rem;
        }}
    }}
    
    /* Animation classes */
    .fade-in {{
        animation: fadeIn 0.5s ease-in;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* Loading animation */
    .loading-spinner {{
        border: 3px solid {Theme.SURFACE_COLOR};
        border-top: 3px solid {Theme.PRIMARY_COLOR};
        border-radius: 50%;
        width: 20px;
        height: 20px;
        animation: spin 1s linear infinite;
    }}
    
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="LinkedIn Post Generator",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/yourusername/linkedin-post-generator',
            'Report a bug': None,
            'About': "AI-powered LinkedIn content generator with clean architecture"
        }
    )


def add_custom_fonts():
    """Add custom fonts if needed."""
    fonts_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    </style>
    """
    st.markdown(fonts_css, unsafe_allow_html=True)


def render_loading_animation():
    """Render a custom loading animation."""
    loading_html = """
    <div style="text-align: center; padding: 2rem;">
        <div class="loading-spinner" style="margin: 0 auto 1rem auto;"></div>
        <p style="color: #666;">Generating your LinkedIn post...</p>
    </div>
    """
    st.markdown(loading_html, unsafe_allow_html=True)


def apply_card_style(content: str, title: str = "") -> str:
    """Wrap content in a styled card."""
    card_html = f"""
    <div class="card fade-in">
        {f'<h3 style="margin-top: 0; color: {Theme.PRIMARY_COLOR};">{title}</h3>' if title else ''}
        {content}
    </div>
    """
    return card_html


def render_section_header(title: str, icon: str = ""):
    """Render a styled section header."""
    st.markdown(f"""
    <div style="margin: 2rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid {Theme.SURFACE_COLOR};">
        <h2 style="margin: 0; color: #333;">
            {icon} {title}
        </h2>
    </div>
    """, unsafe_allow_html=True)


def add_tooltip(text: str, tooltip: str):
    """Add a tooltip to text."""
    tooltip_html = f"""
    <span style="border-bottom: 1px dotted #666; cursor: help;" title="{tooltip}">
        {text}
    </span>
    """
    st.markdown(tooltip_html, unsafe_allow_html=True)
