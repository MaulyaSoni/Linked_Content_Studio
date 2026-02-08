"""
Professional Theme Styling for LinkedIn Post Generator.
Supports Light and Dark modes with Poppins, JakartaSans fonts.
Clean styling without excessive gradients.
"""

import streamlit as st
from typing import Dict, Literal


class ThemeManager:
    """Manage application themes and styling."""
    
    LIGHT_THEME = {
        "primary_bg": "#FFFFFF",
        "secondary_bg": "#F5F7FA",
        "tertiary_bg": "#EFF2F7",
        "primary_text": "#000000",
        "secondary_text": "#333333",
        "tertiary_text": "#666666",
        "accent_color": "#FFD700",
        "accent_hover": "#FFC700",
        "accent2_color": "#DC143C",
        "accent3_color": "#00008B",
        "success_color": "#31A24C",
        "error_color": "#E7113C",
        "warning_color": "#F1A208",
        "border_color": "#D0D7E0",
        "card_shadow": "0 2px 8px rgba(0, 0, 0, 0.12)",
        "button_shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
    }
    
    DARK_THEME = {
        "primary_bg": "#000000",
        "secondary_bg": "#1A1A1A",
        "tertiary_bg": "#252525",
        "primary_text": "#FFD700",
        "secondary_text": "#FFD700",
        "tertiary_text": "#00FFFF",
        "accent_color": "#FFD700",
        "accent_hover": "#FFC700",
        "accent2_color": "#00FFFF",
        "accent3_color": "#FFB6FF",
        "success_color": "#00FF00",
        "error_color": "#FF6B6B",
        "warning_color": "#FFB74D",
        "border_color": "#333333",
        "card_shadow": "0 4px 16px rgba(255, 215, 0, 0.15)",
        "button_shadow": "0 4px 16px rgba(255, 215, 0, 0.2)",
    }
    
    @staticmethod
    def get_current_theme() -> Dict[str, str]:
        """Get current theme based on user selection."""
        theme_mode = st.session_state.get("theme_mode", "light")
        return (
            ThemeManager.LIGHT_THEME
            if theme_mode == "light"
            else ThemeManager.DARK_THEME
        )
    
    @staticmethod
    def apply_custom_css():
        """Apply custom CSS styling with fonts and themes."""
        theme = ThemeManager.get_current_theme()
        theme_mode = st.session_state.get("theme_mode", "light")
        
        main_bg = theme['primary_bg']
        sidebar_bg = theme['secondary_bg']
        
        css = f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            html, body, [data-testid="stAppViewContainer"] {{
                background: {main_bg};
                color: {theme['primary_text']};
            }}
            
            /* Main content area */
            [data-testid="stAppViewContainer"] {{
                background: {main_bg};
            }}
            
            /* Sidebar */
            [data-testid="stSidebar"] {{
                background: {sidebar_bg};
                border-right: 2px solid {theme['border_color']};
            }}
            
            /* Remove header white block */
            [data-testid="stHeader"] {{
                background: transparent;
                border-bottom: none;
            }}
            
            /* Typography - Headings with Poppins */
            h1, h2, h3, h4, h5, h6 {{
                font-family: 'Poppins', sans-serif;
                font-weight: 800;
                letter-spacing: 0.5px;
                text-shadow: none;
            }}
            
            h1 {{
                font-size: 3.5rem;
                margin-bottom: 1.5rem;
                color: {theme['primary_text']};
            }}
            
            h2 {{
                font-size: 2.75rem;
                margin-bottom: 1.2rem;
                color: {theme['primary_text']};
            }}
            
            h3 {{
                font-size: 2.25rem;
                margin-bottom: 1rem;
                color: #FFFFFF;
            }}
            
            h4 {{
                font-size: 1.75rem;
                margin-bottom: 0.8rem;
                color: #FFFFFF;
            }}
            
            /* Body text with Jakarta Sans */
            p, span, div, label {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: 1.1rem;
                color: {theme['primary_text']};
                line-height: 1.8;
            }}
            
            /* Cards and containers */
            [data-testid="stVerticalBlock"] > div {{
                background: transparent;
            }}
            
            [data-testid="stForm"] {{
                background-color: {theme['tertiary_bg']};
                border-radius: 16px;
                padding: 2rem;
                border: 2px solid {theme['border_color']};
                box-shadow: {theme['card_shadow']};
            }}
            
            /* Button styling - Bold Yellow with curve borders */
            button {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-weight: 800;
                font-size: 1.1rem;
                border-radius: 16px;
                padding: 1rem 2rem;
                border: none;
                cursor: pointer;
                box-shadow: {theme['button_shadow']};
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                background-color: {theme['primary_text']};
                color: {theme['primary_bg']};
            }}
            
            button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
                background-color: {theme['accent_hover']};
            }}
            
            button:active {{
                transform: translateY(0);
            }}
            
            /* Primary buttons */
            [data-testid="baseButton-primary"] {{
                background-color: {theme['accent_color']} !important;
                color: {theme['primary_bg']} !important;
                font-weight: 800 !important;
                border-radius: 16px !important;
            }}
            
            [data-testid="baseButton-primary"]:hover {{
                background-color: {theme['accent_hover']} !important;
                box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4) !important;
            }}
            
            /* Secondary buttons */
            [data-testid="baseButton-secondary"] {{
                background-color: {theme['tertiary_bg']} !important;
                color: {theme['primary_text']} !important;
                border: 2px solid {theme['accent_color']} !important;
                font-weight: 800 !important;
                border-radius: 16px !important;
            }}
            
            [data-testid="baseButton-secondary"]:hover {{
                background-color: {theme['accent_color']} !important;
                color: {theme['primary_bg']} !important;
            }}
            
            /* Input fields */
            input, textarea {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                background-color: {theme['tertiary_bg']};
                color: {theme['primary_text']};
                border: 2px solid {theme['border_color']};
                border-radius: 16px;
                padding: 1rem;
                font-size: 1.05rem;
                transition: all 0.3s ease;
            }}
            
            input:focus, textarea:focus {{
                outline: none;
                border-color: {theme['accent_color']};
                box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2);
                background-color: {theme['secondary_bg']};
                transform: translateY(-2px);
            }}
            
            /* Dropdown/Select styling */
            select {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                background-color: {theme['tertiary_bg']} !important;
                color: {theme['primary_text']} !important;
                border: 2px solid {theme['border_color']} !important;
                border-radius: 16px !important;
                padding: 0.8rem !important;
                font-size: 1.05rem !important;
            }}
            
            select:focus {{
                outline: none;
                border-color: {theme['accent_color']} !important;
                box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2) !important;
            }}
            
            /* Text areas */
            textarea {{
                resize: vertical;
                min-height: 120px;
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-weight: 600;
            }}
            
            /* Labels */
            label {{
                font-weight: 800;
                font-family: 'Poppins', sans-serif;
                font-size: 1.15rem;
                color: {theme['primary_text']};
                margin-bottom: 0.8rem;
                display: inline-block;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            /* Input source options (radio buttons) - CYAN */
            [data-testid="stRadio"] {{
                color: #00FFFF;
            }}
            
            [data-testid="stRadio"] label {{
                color: #FFFFFF;
            }}
            
            [data-testid="stRadio"] input[type="radio"] {{
                accent-color: #00FFFF;
            }}
            
            /* Code blocks */
            pre {{
                background-color: {theme['tertiary_bg']};
                border: 2px solid {theme['border_color']};
                border-radius: 16px;
                padding: 1.5rem;
                overflow-x: auto;
            }}
            
            code {{
                font-family: 'Courier New', monospace;
                color: {theme['accent_color']};
                background-color: {theme['tertiary_bg']};
                padding: 0.3em 0.6em;
                border-radius: 8px;
            }}
            
            /* Success messages */
            [data-testid="stSuccess"] {{
                background-color: rgba(0, 255, 0, 0.1);
                border: 2px solid {theme['success_color']};
                border-radius: 16px;
                padding: 1.2rem;
                color: {theme['success_color']};
                font-weight: 600;
            }}
            
            /* Error messages */
            [data-testid="stError"] {{
                background-color: rgba(255, 107, 107, 0.1);
                border: 2px solid {theme['error_color']};
                border-radius: 16px;
                padding: 1.2rem;
                color: {theme['error_color']};
                font-weight: 600;
            }}
            
            /* Warning messages */
            [data-testid="stWarning"] {{
                background-color: rgba(255, 183, 77, 0.1);
                border: 2px solid {theme['warning_color']};
                border-radius: 16px;
                padding: 1.2rem;
                color: {theme['warning_color']};
                font-weight: 600;
            }}
            
            /* Info messages */
            [data-testid="stInfo"] {{
                background-color: rgba(0, 255, 255, 0.1);
                border: 2px solid {theme['accent2_color']};
                border-radius: 16px;
                padding: 1.2rem;
                color: {theme['accent2_color']};
                font-weight: 600;
            }}
            
            /* Expander */
            [data-testid="stExpander"] {{
                background-color: {theme['tertiary_bg']};
                border: 2px solid {theme['border_color']};
                border-radius: 16px;
            }}
            
            /* Divider */
            hr {{
                border: none;
                height: 2px;
                background: linear-gradient(90deg, transparent, {theme['border_color']}, transparent);
                margin: 2rem 0;
            }}
            
            /* Metrics */
            [data-testid="metric-container"] {{
                background-color: {theme['tertiary_bg']};
                border: 2px solid {theme['border_color']};
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: {theme['card_shadow']};
            }}
            
            /* Tables */
            table {{
                background-color: {theme['secondary_bg']};
                border-collapse: collapse;
                width: 100%;
                border-radius: 16px;
                overflow: hidden;
            }}
            
            th {{
                background-color: {theme['tertiary_bg']};
                padding: 1.2rem;
                text-align: left;
                font-weight: 800;
                font-family: 'Poppins', sans-serif;
                border-bottom: 3px solid {theme['border_color']};
                color: {theme['accent_color']};
            }}
            
            td {{
                padding: 1rem;
                border-bottom: 1px solid {theme['border_color']};
                font-family: 'Plus Jakarta Sans', sans-serif;
            }}
            
            tr:hover {{
                background-color: {theme['tertiary_bg']};
            }}
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {{
                width: 12px;
                height: 12px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: {theme['tertiary_bg']};
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {theme['accent_color']};
                border-radius: 6px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: {theme['accent_hover']};
            }}
            
            /* Animations */
            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                }}
                to {{
                    opacity: 1;
                }}
            }}
            
            [data-testid="stMetricLabel"] {{
                animation: fadeIn 0.3s ease-in;
            }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    @staticmethod
    def render_theme_selector():
        """Render theme toggle in sidebar with proper styling."""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎨 Theme Mode")
        
        # Get theme for buttons
        theme_mode = st.session_state.get("theme_mode", "light")
        
        theme_col1, theme_col2 = st.sidebar.columns(2)
        
        with theme_col1:
            if st.button("☀️ Light", use_container_width=True, key="light_theme_btn"):
                st.session_state.theme_mode = "light"
                st.rerun()
        
        with theme_col2:
            if st.button("🌙 Dark", use_container_width=True, key="dark_theme_btn"):
                st.session_state.theme_mode = "dark"
                st.rerun()
        
        st.sidebar.caption(f"✨ Current: **{theme_mode.capitalize()}** Mode")
