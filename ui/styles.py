"""
UI Styles - Premium Theme System
=================================
Dark / Light mode with bold colors, gradient headings, Jakarta Sans + Poppins fonts,
gear-based loading animations, and polished borders & buttons.
"""

import streamlit as st


# ═══════════════════════════════════════════════════════════════════════════
# THEME CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class ThemeLight:
    """Light-mode palette — bold black / blue / red accents."""
    NAME = "light"
    BG              = "#FFFFFF"
    BG_SECONDARY    = "#F5F7FA"
    SURFACE         = "#FFFFFF"
    SURFACE_BORDER  = "#E2E8F0"
    TEXT            = "#111827"
    TEXT_MUTED      = "#6B7280"

    PRIMARY         = "#1D4ED8"   # Bold blue
    PRIMARY_HOVER   = "#1E40AF"
    ACCENT_RED      = "#DC2626"
    ACCENT_BLACK    = "#111827"
    ACCENT_CYAN     = "#06B6D4"

    BTN_1_BG = ACCENT_RED;    BTN_1_FG = "#FFFFFF"   # red-white
    BTN_2_BG = ACCENT_BLACK;  BTN_2_FG = "#FFFFFF"   # black-white
    BTN_3_BG = PRIMARY;       BTN_3_FG = ACCENT_CYAN # blue-cyan
    BTN_4_BG = "#FFFFFF";     BTN_4_FG = ACCENT_RED  # white-red

    GRADIENT_START  = "#1D4ED8"
    GRADIENT_MID    = "#DC2626"
    GRADIENT_END    = "#111827"

    SUCCESS  = "#16A34A"
    WARNING  = "#D97706"
    ERROR    = "#DC2626"


class ThemeDark:
    """Dark-mode palette — formal matte deep-blue / slate / white. No neon gradients."""
    NAME = "dark"
    BG              = "#0D1117"   # GitHub-dark charcoal
    BG_SECONDARY    = "#161B22"   # slightly lighter surface
    SURFACE         = "#1C2128"   # card surface
    SURFACE_BORDER  = "#30363D"   # subtle slate border
    TEXT            = "#E6EDF3"   # near-white readable text
    TEXT_MUTED      = "#7D8590"   # muted slate

    PRIMARY         = "#4D9FFF"   # bold matte blue (no neon)
    PRIMARY_HOVER   = "#3887EB"
    ACCENT_RED      = "#F85149"   # flat red
    ACCENT_BLACK    = "#CDD9E5"   # near-white on dark
    ACCENT_CYAN     = "#79C0FF"   # soft cool blue (replaces neon cyan)

    BTN_1_BG = "#4D9FFF";    BTN_1_FG = "#0D1117"   # blue-dark
    BTN_2_BG = "#CDD9E5";    BTN_2_FG = "#0D1117"   # white-dark
    BTN_3_BG = "#F85149";    BTN_3_FG = "#E6EDF3"   # red-light
    BTN_4_BG = "#1C2128";    BTN_4_FG = "#4D9FFF"   # surface-blue

    GRADIENT_START  = "#4D9FFF"   # all same → single solid tone (no rainbow)
    GRADIENT_MID    = "#79C0FF"
    GRADIENT_END    = "#4D9FFF"

    SUCCESS  = "#3FB950"   # matte green
    WARNING  = "#D29922"   # muted amber
    ERROR    = "#F85149"   # flat red


def _get_theme():
    """Return the active theme object based on session-state toggle."""
    if st.session_state.get("dark_mode", False):
        return ThemeDark
    return ThemeLight


# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════

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
            'About': "AI-powered LinkedIn content generator — bold, modern, beautiful."
        }
    )


# ═══════════════════════════════════════════════════════════════════════════
# MASTER CSS
# ═══════════════════════════════════════════════════════════════════════════

def apply_custom_css():
    """Inject the full custom CSS (adapts to current theme)."""
    T = _get_theme()

    css = f"""
    <style>
    /* ── FONTS ─────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Poppins:wght@300;400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    :root {{
        --bg:             {T.BG};
        --bg2:            {T.BG_SECONDARY};
        --surface:        {T.SURFACE};
        --border:         {T.SURFACE_BORDER};
        --text:           {T.TEXT};
        --text-muted:     {T.TEXT_MUTED};
        --primary:        {T.PRIMARY};
        --primary-hover:  {T.PRIMARY_HOVER};
        --accent-red:     {T.ACCENT_RED};
        --accent-cyan:    {T.ACCENT_CYAN};
        --success:        {T.SUCCESS};
        --warning:        {T.WARNING};
        --error:          {T.ERROR};
        --grad-start:     {T.GRADIENT_START};
        --grad-mid:       {T.GRADIENT_MID};
        --grad-end:       {T.GRADIENT_END};
    }}

    /* ── BASE ──────────────────────────────────────────────── */
    .stApp {{
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Poppins', sans-serif !important;
    }}

    h1, h2, h3, h4, .stButton > button,
    .mode-card-title, .section-title {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
    }}

    p, span, label, .stTextInput label, .stSelectbox label,
    .stTextArea label, .stMarkdown, li {{
        font-family: 'Poppins', sans-serif !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }}

    /* Re-allow gradient titles to override the above safely */
    /* ── HEADINGS — gradient in light, bold solid in dark ────── */
    .gradient-title {{
        {'color: ' + T.PRIMARY + ' !important; background: none !important; -webkit-text-fill-color: ' + T.PRIMARY + ' !important;' if T.NAME == 'dark' else
         'background: linear-gradient(135deg, var(--grad-start), var(--grad-mid), var(--grad-end)) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; background-clip: text !important;'}
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        letter-spacing: -0.02em;
    }}
    /* Child elements of gradient-title inherit the transparent fill in light mode */
    .gradient-title span:not(.gt-icon),
    .gradient-title h1, .gradient-title h2, .gradient-title h3 {{
        {'color: ' + T.PRIMARY + ' !important; -webkit-text-fill-color: ' + T.PRIMARY + ' !important;' if T.NAME == 'dark' else
         '-webkit-text-fill-color: transparent !important; background-clip: text !important; -webkit-background-clip: text !important;'}
    }}

    .gradient-title-lg {{
        font-size: 2.8rem;
        line-height: 1.15;
    }}

    .gradient-title-md {{
        font-size: 1.6rem;
        line-height: 1.3;
    }}

    .gradient-title-sm {{
        font-size: 1.15rem;
        line-height: 1.35;
    }}

    /* ── BUTTONS (global) ──────────────────────────────────── */
    .stButton > button {{
        font-size: 1.3rem !important;
        padding: 0.65rem 1.6rem !important;
        border-radius: 14px !important;
        border: 2px solid var(--border) !important;
        font-weight: 700 !important;
        transition: all 0.25s cubic-bezier(.4,0,.2,1) !important;
        letter-spacing: 0.01em;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
    }}

    /* Primary button — flat in dark, gradient in light */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {{
        background: {f'{T.BTN_1_BG}' if T.NAME == 'dark' else f'linear-gradient(135deg, {T.BTN_1_BG}, {T.PRIMARY})'} !important;
        color: {T.BTN_1_FG} !important;
        border: {'2px solid ' + T.PRIMARY if T.NAME == 'dark' else 'none'} !important;
        font-size: 1.5rem !important;
        padding: 0.75rem 2rem !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {{
        background: {T.PRIMARY_HOVER} !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35) !important;
    }}

    /* Secondary buttons */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="stBaseButton-secondary"] {{
        background: {T.BTN_2_BG} !important;
        color: {T.BTN_2_FG} !important;
        border: 2px solid {T.BTN_2_BG} !important;
    }}
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="stBaseButton-secondary"]:hover {{
        background: transparent !important;
        color: {T.BTN_2_BG} !important;
    }}

    /* ── INPUT FIELDS ──────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Poppins', sans-serif !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(29,78,216,0.15) !important;
    }}

    /* ── CARDS ─────────────────────────────────────────────── */
    .premium-card {{
        background: var(--surface);
        border: 2px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }}
    .premium-card:hover {{
        border-color: var(--primary);
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }}

    /* ── MODE SELECTOR CARDS ──────────────────────────────── */
    .mode-card {{
        background: var(--surface);
        border: 2px solid var(--border);
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    .mode-card:hover {{
        border-color: var(--primary);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        transform: translateY(-3px);
    }}
    .mode-card.active {{
        border-color: var(--primary);
        background: {'var(--primary)' if T.NAME == 'dark' else 'linear-gradient(135deg, var(--primary), var(--grad-mid))'};
        color: {'var(--bg)' if T.NAME == 'dark' else 'white'} !important;
    }}
    .mode-card-title {{
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0.5rem 0 0.25rem 0;
    }}
    .mode-card-desc {{
        font-size: 0.85rem;
        color: var(--text-muted);
    }}

    /* ── METRICS ───────────────────────────────────────────── */
    div[data-testid="stMetric"],
    .stMetric {{
        background: var(--surface) !important;
        border: 2px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 1rem !important;
        text-align: center !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 800 !important;
        color: var(--primary) !important;
    }}

    /* ── EXPANDER ──────────────────────────────────────────── */
    .streamlit-expanderHeader,
    [data-testid="stExpander"] > details > summary {{
        background-color: var(--bg2) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }}
    /* Fix expander toggle arrow rendering as raw "arrow_right" text */
    [data-testid="stExpander"] details summary span,
    [data-testid="stExpanderToggleIcon"],
    details summary .st-emotion-cache-1h9usn1,
    details > summary > span {{
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
        font-size: 1.2rem !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        background: none !important;
        background-clip: initial !important;
        -webkit-background-clip: initial !important;
    }}

    /* ── TOP HEADER BAR (white stripe fix) ─────────────────── */
    header[data-testid="stHeader"] {{
        background-color: var(--bg) !important;
        border-bottom: 1px solid var(--border) !important;
    }}
    .stAppHeader {{
        background-color: var(--bg) !important;
    }}
    /* Toolbar buttons inside header */
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] a {{
        color: var(--text) !important;
    }}

    /* ── SIDEBAR ───────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg2) !important;
        border-right: 2px solid var(--border) !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown {{
        color: var(--text) !important;
    }}

    /* ── TABS ──────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 12px 12px 0 0;
        padding: 0.6rem 1.2rem;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600;
        border: 2px solid var(--border);
        border-bottom: none;
        background: var(--bg2);
        transition: all 0.2s ease;
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--surface) !important;
        border-color: var(--primary) !important;
        color: var(--primary) !important;
    }}

    /* ── RADIO / CHECKBOX ─────────────────────────────────── */
    .stRadio > label, .stCheckbox > label {{
        font-family: 'Poppins', sans-serif !important;
    }}
    .stRadio > div[role="radiogroup"] > label {{
        background: var(--surface) !important;
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
        margin-right: 0.5rem !important;
        transition: all 0.2s ease !important;
    }}
    .stRadio > div[role="radiogroup"] > label:hover {{
        border-color: var(--primary) !important;
    }}
    .stRadio > div[role="radiogroup"] > label[data-checked="true"] {{
        border-color: var(--primary) !important;
        background: {'var(--primary)' if T.NAME == 'dark' else 'linear-gradient(135deg, var(--primary), var(--grad-mid))'} !important;
        color: var(--bg) !important;
    }}

    /* ── DIVIDER ───────────────────────────────────────────── */
    hr {{
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, var(--border), transparent) !important;
        margin: 1.5rem 0 !important;
    }}

    /* ── CODE BLOCK (post preview) ─────────────────────────── */
    .stCode, pre {{
        background-color: var(--bg2) !important;
        border: 2px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 1.25rem !important;
        font-family: 'Poppins', sans-serif !important;
        color: var(--text) !important;
    }}

    /* ── TOAST / ALERTS ────────────────────────────────────── */
    .stSuccess {{
        background: linear-gradient(90deg, rgba(22,163,74,0.08), rgba(22,163,74,0.02)) !important;
        border-left: 5px solid var(--success) !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
    }}
    .stError {{
        background: linear-gradient(90deg, rgba(220,38,38,0.08), rgba(220,38,38,0.02)) !important;
        border-left: 5px solid var(--error) !important;
        border-radius: 12px !important;
    }}
    .stWarning {{
        background: linear-gradient(90deg, rgba(217,119,6,0.08), rgba(217,119,6,0.02)) !important;
        border-left: 5px solid var(--warning) !important;
        border-radius: 12px !important;
    }}
    .stInfo {{
        background: linear-gradient(90deg, rgba(29,78,216,0.08), rgba(29,78,216,0.02)) !important;
        border-left: 5px solid var(--primary) !important;
        border-radius: 12px !important;
    }}

    /* ── PROGRESS BAR ──────────────────────────────────────── */
    .stProgress > div > div > div {{
        background: {'var(--primary)' if T.NAME == 'dark' else 'linear-gradient(90deg, var(--grad-start), var(--grad-mid), var(--grad-end))'} !important;
        border-radius: 8px !important;
    }}

    /* ── SCROLLBAR ─────────────────────────────────────────── */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--bg2);
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border);
        border-radius: 8px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--primary);
    }}

    /* ── ANIMATION HELPERS ─────────────────────────────────── */
    .fade-in {{
        animation: fadeIn 0.5s ease-in;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .slide-up {{
        animation: slideUp 0.6s ease-out;
    }}
    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ── RESPONSIVE ────────────────────────────────────────── */
    @media (max-width: 768px) {{
        .stButton > button {{
            font-size: 1.1rem !important;
            padding: 0.55rem 1rem !important;
            border-radius: 12px !important;
        }}
        .gradient-title-lg {{
            font-size: 2rem;
        }}
    }}

    /* ── MATERIAL SYMBOLS — sidebar collapse icon ──────────── */
    .material-symbols-rounded,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="collapsedControl"] span,
    button[data-testid="baseButton-headerNoPadding"] span {{
        font-family: 'Material Symbols Rounded' !important;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
    }}

    /* ── GRADIENT TITLE ICON — resets emoji/icon inside gradient text ── */
    .gt-icon {{
        -webkit-text-fill-color: initial !important;
        background: none !important;
        -webkit-background-clip: initial !important;
        background-clip: initial !important;
        display: inline;
    }}

    /* ── ENHANCED INPUT FIELDS (dark mode compatible) ────────── */
    [data-baseweb="base-input"] {{
        background-color: var(--surface) !important;
        border-color: var(--border) !important;
    }}
    [data-baseweb="base-input"] > div,
    [data-baseweb="base-input"] input,
    [data-baseweb="base-input"] textarea {{
        background-color: var(--surface) !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        caret-color: var(--primary) !important;
    }}

    /* ── SELECT BOX — control wrapper ───────────────────────── */
    div[data-baseweb="select"] > div,
    .stSelectbox > div > div {{
        background-color: {T.SURFACE} !important;
        border: 1.5px solid {T.SURFACE_BORDER} !important;
        border-radius: 12px !important;
    }}

    /* ── SELECT BOX — ULTRA-SPECIFICITY text color fix ────────
       Class-repetition trick (.cls.cls.cls) triples CSS
       specificity to always beat Emotion's generated classes.
       Hardcoded hex avoids var() resolution failures.          */
    .stSelectbox.stSelectbox.stSelectbox [data-baseweb="select"] div,
    .stSelectbox.stSelectbox.stSelectbox [data-baseweb="select"] span,
    .stSelectbox.stSelectbox.stSelectbox [data-baseweb="select"] p,
    .stSelectbox.stSelectbox.stSelectbox [data-baseweb="select"] [class*="css-"],
    .stSelectbox.stSelectbox.stSelectbox [data-baseweb="select"] [class*="st-"],
    .stMultiSelect.stMultiSelect.stMultiSelect [data-baseweb="select"] div,
    .stMultiSelect.stMultiSelect.stMultiSelect [data-baseweb="select"] span,
    div[data-baseweb="select"][data-baseweb="select"][data-baseweb="select"] div,
    div[data-baseweb="select"][data-baseweb="select"][data-baseweb="select"] span,
    div[data-baseweb="select"][data-baseweb="select"][data-baseweb="select"] [class*="css-"] {{
        color: {T.TEXT} !important;
        -webkit-text-fill-color: {T.TEXT} !important;
        opacity: 1 !important;
        visibility: visible !important;
        background: transparent !important;
        background-clip: initial !important;
        -webkit-background-clip: initial !important;
    }}

    /* Re-apply surface BG to outer control only */
    .stSelectbox.stSelectbox.stSelectbox [data-baseweb="select"] > div {{
        background-color: {T.SURFACE} !important;
    }}

    /* ── SELECT BOX — placeholder text ───────────────────────── */
    .stSelectbox.stSelectbox.stSelectbox [data-baseweb="select-placeholder"],
    .stSelectbox.stSelectbox.stSelectbox [data-baseweb="select-placeholder"] * {{
        color: {T.TEXT_MUTED} !important;
        -webkit-text-fill-color: {T.TEXT_MUTED} !important;
    }}

    /* ── SELECT BOX — SVG chevron ────────────────────────────── */
    div[data-baseweb="select"] svg,
    div[data-baseweb="select"] svg path {{
        fill: {T.TEXT_MUTED} !important;
        color: {T.TEXT_MUTED} !important;
        -webkit-text-fill-color: unset !important;
    }}

    input::placeholder,
    textarea::placeholder {{
        color: var(--text-muted) !important;
        -webkit-text-fill-color: var(--text-muted) !important;
        opacity: 1 !important;
    }}

    /* ── DROPDOWN POPUP / POPOVER ─────────────────────────── */
    [data-baseweb="popover"] > div,
    [data-baseweb="popover"] [data-baseweb="menu"],
    [data-baseweb="popover"] ul {{
        background-color: {T.SURFACE} !important;
        border: 1px solid {T.SURFACE_BORDER} !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 28px rgba(0,0,0,0.35) !important;
    }}
    [data-baseweb="option"],
    li[role="option"],
    ul[role="listbox"] li {{
        background-color: {T.SURFACE} !important;
        color: {T.TEXT} !important;
        -webkit-text-fill-color: {T.TEXT} !important;
        font-family: 'Poppins', sans-serif !important;
        cursor: pointer !important;
        padding: 10px 15px !important;
        margin: 2px 5px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }}
    [data-baseweb="option"] *,
    li[role="option"] * {{
        color: {T.TEXT} !important;
        -webkit-text-fill-color: {T.TEXT} !important;
    }}
    [data-baseweb="option"]:hover,
    li[role="option"]:hover {{
        background-color: {T.BG_SECONDARY} !important;
        color: {T.PRIMARY} !important;
        -webkit-text-fill-color: {T.PRIMARY} !important;
        transform: translateX(4px) !important;
    }}
    [data-baseweb="option"]:hover *,
    li[role="option"]:hover * {{
        color: {T.PRIMARY} !important;
        -webkit-text-fill-color: {T.PRIMARY} !important;
    }}
    [aria-selected="true"][data-baseweb="option"],
    [aria-selected="true"][data-baseweb="option"] * {{
        background-color: {T.BG_SECONDARY} !important;
        color: {T.PRIMARY} !important;
        -webkit-text-fill-color: {T.PRIMARY} !important;
        font-weight: 600 !important;
    }}

    /* ── FILE UPLOADER ──────────────────────────────────────── */
    [data-testid="stFileUploader"] {{
        background-color: var(--surface) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stFileUploaderDropzone"] {{
        background-color: var(--bg2) !important;
        border: 2px dashed var(--border) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] small {{
        color: var(--text-muted) !important;
    }}
    [data-testid="stFileUploaderDropzone"] button {{
        background-color: var(--surface) !important;
        color: var(--primary) !important;
        border: 1px solid var(--primary) !important;
    }}

    /* ── CURSOR: POINTER ON ALL DROPDOWNS & SELECTS ─────────── */
    .stSelectbox,
    .stSelectbox > div,
    .stSelectbox > div > div,
    .stSelectbox > div > div > div,
    .stSelectbox svg,
    [data-baseweb="select"] > div,
    [data-baseweb="option"],
    [role="option"],
    [role="listbox"] li,
    .stDateInput,
    .stTimeInput,
    .stMultiSelect > div > div,
    .stSlider > div > div {{
        cursor: pointer !important;
    }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # ── JavaScript fix: force selectbox value text visibility ──────────
    # Streamlit's Emotion CSS-in-JS engine injects styles AFTER our
    # stylesheet, which can override even !important rules.
    # This script patches the DOM directly after every render.
    T2 = _get_theme()
    st.html(f"""
    <script>
    (function() {{
        var TEXT   = "{T2.TEXT}";
        var MUTED  = "{T2.TEXT_MUTED}";
        var SURF   = "{T2.SURFACE}";
        var BORDER = "{T2.SURFACE_BORDER}";

        function fixAllSelects() {{
            document.querySelectorAll('[data-baseweb="select"]').forEach(function(sel) {{
                // Fix the outer control background
                var ctrl = sel.querySelector(':scope > div');
                if (ctrl) {{
                    ctrl.style.setProperty('background-color', SURF, 'important');
                    ctrl.style.setProperty('border-color', BORDER, 'important');
                    ctrl.style.setProperty('border-radius', '12px', 'important');
                }}

                // Fix ALL inner text elements (spans, divs, etc.)
                sel.querySelectorAll('div, span, p').forEach(function(el) {{
                    el.style.setProperty('color', TEXT, 'important');
                    el.style.setProperty('-webkit-text-fill-color', TEXT, 'important');
                    el.style.setProperty('opacity', '1', 'important');
                }});

                // Fix SVG chevron separately
                sel.querySelectorAll('svg, path').forEach(function(svg) {{
                    svg.style.setProperty('fill', MUTED, 'important');
                }});
            }});
        }}

        // Run immediately
        fixAllSelects();

        // Run on every DOM mutation (handles Streamlit re-renders)
        var debounce = null;
        var observer = new MutationObserver(function() {{
            clearTimeout(debounce);
            debounce = setTimeout(fixAllSelects, 50);
        }});
        observer.observe(document.body, {{
            childList: true, subtree: true,
            attributes: true, attributeFilter: ['class', 'style']
        }});

        // Also run on an interval as a safety net
        setInterval(fixAllSelects, 500);
    }})();
    </script>
    """)


# ═══════════════════════════════════════════════════════════════════════════
# LOADING ANIMATIONS — Next-level gear / circle
# ═══════════════════════════════════════════════════════════════════════════

def render_loading_animation(message: str = "Generating your LinkedIn post…"):
    """Render a premium gear + 100% progress-circle loading animation with blurred backdrop."""
    T = _get_theme()
    bg_rgba = '13,17,23' if T.NAME == 'dark' else '255,255,255'
    loading_html = f"""
    <style>
    .loading-overlay {{
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba({bg_rgba}, 0.85);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        z-index: 99999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    .gear svg {{
        animation: gearSpin 2.5s linear infinite;
    }}
    .gear.reverse svg {{
        animation: gearSpinReverse 2.5s linear infinite;
    }}
    @keyframes gearSpin {{
        from {{ transform: rotate(0deg); }}
        to   {{ transform: rotate(360deg); }}
    }}
    @keyframes gearSpinReverse {{
        from {{ transform: rotate(0deg); }}
        to   {{ transform: rotate(-360deg); }}
    }}
    .progress-ring svg {{
        transform: rotate(-90deg);
    }}
    .progress-ring circle {{
        fill: none;
        stroke-width: 6;
        stroke-linecap: round;
    }}
    .progress-ring .bg {{
        stroke: {T.SURFACE_BORDER};
    }}
    .progress-ring .fg {{
        stroke: url(#loadGrad);
        stroke-dasharray: 339.292;
        animation: circleProgress 2.2s ease-in-out infinite;
    }}
    @keyframes circleProgress {{
        0%   {{ stroke-dashoffset: 339.292; }}
        50%  {{ stroke-dashoffset: 40; }}
        100% {{ stroke-dashoffset: 339.292; }}
    }}
    .loading-text {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        margin-top: 1.5rem;
        color: {T.TEXT};
    }}
    .loading-sub {{
        font-family: 'Poppins', sans-serif;
        font-size: 0.9rem;
        color: {T.TEXT_MUTED};
        margin-top: 0.4rem;
    }}
    </style>

    <div class="loading-overlay">
        <div style="display:flex;align-items:center;gap:4px;margin-bottom:1rem;">
            <div class="gear" style="width:60px;height:60px;">
                <svg viewBox="0 0 100 100" width="60" height="60">
                    <path d="M50 15 L54 5 L46 5 Z M50 85 L54 95 L46 95 Z M15 50 L5 46 L5 54 Z M85 50 L95 54 L95 46 Z
                             M22 22 L14 17 L17 14 Z M78 22 L83 14 L86 17 Z M22 78 L17 86 L14 83 Z M78 78 L86 83 L83 86 Z"
                          fill="{T.PRIMARY}"/>
                    <circle cx="50" cy="50" r="25" fill="{T.PRIMARY}" opacity="0.85"/>
                    <circle cx="50" cy="50" r="12" fill="{T.SURFACE}"/>
                </svg>
            </div>
            <div class="gear reverse" style="width:40px;height:40px;margin-top:10px;">
                <svg viewBox="0 0 100 100" width="40" height="40">
                    <path d="M50 15 L54 5 L46 5 Z M50 85 L54 95 L46 95 Z M15 50 L5 46 L5 54 Z M85 50 L95 54 L95 46 Z
                             M22 22 L14 17 L17 14 Z M78 22 L83 14 L86 17 Z M22 78 L17 86 L14 83 Z M78 78 L86 83 L83 86 Z"
                          fill="{T.ACCENT_CYAN}"/>
                    <circle cx="50" cy="50" r="25" fill="{T.ACCENT_CYAN}" opacity="0.85"/>
                    <circle cx="50" cy="50" r="12" fill="{T.SURFACE}"/>
                </svg>
            </div>
        </div>

        <div class="progress-ring" style="width:120px;height:120px;">
            <svg width="120" height="120">
                <defs>
                    <linearGradient id="loadGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="{T.GRADIENT_START}"/>
                        <stop offset="50%" stop-color="{T.GRADIENT_MID}"/>
                        <stop offset="100%" stop-color="{T.GRADIENT_END}"/>
                    </linearGradient>
                </defs>
                <circle class="bg" cx="60" cy="60" r="54"/>
                <circle class="fg" cx="60" cy="60" r="54"/>
            </svg>
        </div>

        <div class="loading-text">{message}</div>
        <div class="loading-sub">Please wait — AI agents at work</div>
    </div>
    """
    return st.markdown(loading_html, unsafe_allow_html=True)


def render_inline_loader(message: str = "Processing…"):
    """A smaller inline gear loader for within-page spinners."""
    T = _get_theme()
    html = f"""
    <div style="display:flex;align-items:center;gap:12px;padding:1rem 0;">
        <svg width="32" height="32" viewBox="0 0 100 100" style="animation: gearSpin 2s linear infinite;">
            <style>@keyframes gearSpin {{ from{{transform:rotate(0)}} to{{transform:rotate(360deg)}} }}</style>
            <path d="M50 15 L54 5 L46 5 Z M50 85 L54 95 L46 95 Z M15 50 L5 46 L5 54 Z M85 50 L95 54 L95 46 Z
                     M22 22 L14 17 L17 14 Z M78 22 L83 14 L86 17 Z M22 78 L17 86 L14 83 Z M78 78 L86 83 L83 86 Z"
                  fill="{T.PRIMARY}"/>
            <circle cx="50" cy="50" r="25" fill="{T.PRIMARY}" opacity="0.85"/>
            <circle cx="50" cy="50" r="12" fill="{T.SURFACE}"/>
        </svg>
        <span style="font-family:'Poppins',sans-serif;color:{T.TEXT};font-size:1rem;">{message}</span>
    </div>
    """
    return st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER RENDERERS
# ═══════════════════════════════════════════════════════════════════════════

def apply_card_style(content: str, title: str = "") -> str:
    """Wrap content in a styled premium card."""
    return f"""
    <div class="premium-card fade-in">
        {f'<h3 class="gradient-title gradient-title-md" style="margin-top:0;">{title}</h3>' if title else ''}
        {content}
    </div>
    """


def render_section_header(title: str, icon: str = ""):
    """Render a styled section header with gradient underline."""
    T = _get_theme()
    border_val = f'3px solid {T.PRIMARY}' if T.NAME == 'dark' else '3px solid transparent'
    border_img = '' if T.NAME == 'dark' else f'border-image:linear-gradient(90deg,{T.GRADIENT_START},{T.GRADIENT_MID},{T.GRADIENT_END}) 1;'
    icon_html = f'<span class="gt-icon" style="margin-right:0.3em;">{icon}</span>' if icon else ''
    st.markdown(f"""
    <div style="margin:2rem 0 1rem 0;padding-bottom:0.5rem;
                border-bottom:{border_val};
                {border_img}">
        <h2 class="gradient-title gradient-title-md" style="margin:0;">
            {icon_html}{title}
        </h2>
    </div>
    """, unsafe_allow_html=True)


def render_theme_toggle():
    """Render the dark/light mode toggle in sidebar."""
    dark = st.sidebar.toggle(
        "🌙 Dark Mode",
        value=st.session_state.get("dark_mode", False),
        key="dark_mode_toggle"
    )
    if dark != st.session_state.get("dark_mode", False):
        st.session_state["dark_mode"] = dark
        st.rerun()


def add_tooltip(text: str, tooltip: str):
    """Add a tooltip to text."""
    st.markdown(f"""
    <span style="border-bottom:1px dotted var(--text-muted);cursor:help;" title="{tooltip}">
        {text}
    </span>
    """, unsafe_allow_html=True)


def get_mode_color(mode_name: str) -> str:
    """Return an accent colour for a generation mode — for presentation cards."""
    T = _get_theme()
    mode_colors = {
        "simple":      T.PRIMARY,
        "advanced":    T.ACCENT_CYAN,
        "hackathon":   T.ACCENT_RED,
        "agentic":     T.GRADIENT_MID,
        "storyteller": T.PRIMARY,
        "strategist":  T.ACCENT_CYAN,
        "provocateur": T.ACCENT_RED,
    }
    return mode_colors.get(mode_name.lower(), T.PRIMARY)
