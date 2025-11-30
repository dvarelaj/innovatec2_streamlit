import streamlit as st

# === Color Palette ===
PRIMARY_BLUE = "#0056D6"  # Main corporate blue (buttons, titles)
SECONDARY_BLUE = "#0078FF"  # Lighter blue (links, highlights)
LIGHT_BLUE = "#E8F0FE"  # Background tint (cards, soft areas)
YELLOW_ACCENT = "#E8E000"  # Bright yellow accent (buttons)
LIGHT_GRAY = "#F7F9FB"  # App background
DARK_GRAY = "#333333"  # Text color
MID_GRAY = "#7A7A7A"  # Secondary text
WHITE = "#FFFFFF"  # White elements


# -------------------------------------------------------------------------
def style_layout():
    """Apply global layout styles: background color, text font, and spacing."""
    st.markdown(
        f"""
        <style>
        body {{
            background-color: {LIGHT_GRAY};
            color: {DARK_GRAY};
            font-family: 'Segoe UI', Roboto, sans-serif;
        }}

        .block-container {{
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_header_footer():
    """Hide Streamlit menu and footer, keep header visible."""
    st.markdown(
        """
        <style>
        MainMenu {visibility: hidden;}
        header {visibility: visible;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_buttons():
    """Customize primary, secondary, and sidebar buttons with rounded edges and transitions."""
    st.markdown(
        f"""
        <style>
        /* === General buttons === */
        div.stButton > button:first-child,
        div[data-testid="baseButton-secondary"],
        div[data-testid="baseButton-primary"],
        .stButton > button {{
            background-color: {SECONDARY_BLUE} !important;
            color: {WHITE} !important;
            border-radius: 15px !important;
            padding: 0.6em 1.4em !important;
            border: none !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.15) !important;
        }}

        /* Ensure text color remains white in all states */
        div.stButton > button p,
        div.stButton > button span,
        .stButton > button * {{
            color: {WHITE} !important;
        }}
        
        /* Hover effects */
       div.stButton > button:hover,
        div[data-testid="baseButton-secondary"]:hover,
        div[data-testid="baseButton-primary"]:hover {{
            background-color: {PRIMARY_BLUE} !important;
            transform: scale(1.03);
        }}
        /* === Download buttons === */
        .stDownloadButton > button {{
            background-color: {YELLOW_ACCENT};
            color: {DARK_GRAY};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_sidebar():
    """Style sidebar area: background, button color, and spacing."""
    st.markdown(
        f"""
        <style>
        section[data-testid="stSidebar"] {{
            background-color: {LIGHT_BLUE};
            color: {DARK_GRAY};
        }}
        section[data-testid="stSidebar"] .stButton > button {{
            background-color: {PRIMARY_BLUE};
            color: {WHITE};
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_inputs():
    """Apply uniform style for input fields like text, select, and text areas."""
    st.markdown(
        """
        <style>
        input, textarea, select {{
            border-radius: 8px !important;
            padding: 1em !important;
            transition: 0.3s;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_headings():
    """Set consistent heading colors and font weights."""
    st.markdown(
        f"""
        <style>
        h1, h2, h3 {{
            color: {PRIMARY_BLUE};
            font-weight: 700;
        }}
        p {{
            color: {DARK_GRAY};
        }}
        small, span {{
            color: {MID_GRAY};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_cards():
    """Add card-like styling for containers or dataframes (soft shadow and rounded corners)."""
    st.markdown(
        f"""
        <style>
        .stDataFrame, .stTable {{
            border-radius: 12px;
            background-color: {WHITE};
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        }}
        div[data-testid="stVerticalBlock"] {{
            background-color: {WHITE};
            border-radius: 12px;
            padding: 1.5em;
            margin-bottom: 1em;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_scrollbar():
    """Customize scrollbar style for a modern look."""
    st.markdown(
        f"""
        <style>
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        ::-webkit-scrollbar-thumb {{
            background: {PRIMARY_BLUE};
            border-radius: 4px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def general_style_orch():
    """Orchestrate all style functions to apply the full visual theme."""
    style_layout()
    style_header_footer()
    style_buttons()
    style_sidebar()
    style_inputs()
    style_headings()
    # style_cards()
    style_scrollbar()
