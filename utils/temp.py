import streamlit as st

# === 🎨 COLOR PALETTE (LIGHT MODE) ===
PRIMARY_BLUE = "#0056D6"
SECONDARY_BLUE = "#0078FF"
LIGHT_BLUE = "#E8F0FE"
YELLOW_ACCENT = "#E8E000"
LIGHT_GRAY = "#F7F9FB"
DARK_GRAY = "#333333"
MID_GRAY = "#7A7A7A"
WHITE = "#FFFFFF"

# === 🎨 COLOR PALETTE (DARK MODE) ===
DARK_BG = "#0E1117"
DARK_CARD = "#1E1E26"
DARK_TEXT = "#E4E6EB"
DARK_SECONDARY = "#9CA3AF"
DARK_ACCENT = "#0078FF"


# -------------------------------------------------------------------------
def style_layout(dark=False):
    """Apply layout styles: background, font, and container width."""
    bg_color = DARK_BG if dark else LIGHT_GRAY
    text_color = DARK_TEXT if dark else DARK_GRAY
    st.markdown(
        f"""
        <style>
        body {{
            background-color: {bg_color};
            color: {text_color};
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
    """Hide Streamlit menu and footer."""
    st.markdown(
        """
        <style>
        MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: visible;}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_buttons(dark=False):
    """Style all buttons (primary, download, sidebar, etc.)"""
    if dark:
        base_color = DARK_ACCENT
        hover_color = "#1C9EFF"
        text_color = WHITE
        shadow = "rgba(0,0,0,0.6)"
    else:
        base_color = PRIMARY_BLUE
        hover_color = SECONDARY_BLUE
        text_color = WHITE
        shadow = "rgba(0,0,0,0.2)"

    st.markdown(
        f"""
        <style>
        .stButton > button {{
            background-color: {base_color};
            color: {text_color};
            border-radius: 10px;
            padding: 0.6em 1.4em;
            border: none;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 2px 2px 6px {shadow};
        }}
        .stButton > button:hover {{
            background-color: {hover_color};
            transform: scale(1.03);
        }}
        .stDownloadButton > button {{
            background-color: {YELLOW_ACCENT if not dark else "#FFCA28"};
            color: {DARK_GRAY if not dark else DARK_BG};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_sidebar(dark=False):
    """Customize sidebar background and inner button colors."""
    bg_color = "#161B22" if dark else LIGHT_BLUE
    text_color = DARK_TEXT if dark else DARK_GRAY
    btn_bg = DARK_ACCENT if dark else PRIMARY_BLUE

    st.markdown(
        f"""
        <style>
        section[data-testid="stSidebar"] {{
            background-color: {bg_color};
            color: {text_color};
        }}
        section[data-testid="stSidebar"] .stButton > button {{
            background-color: {btn_bg};
            color: white;
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_inputs(dark=False):
    """Style input fields (text, select, textarea)."""
    border_color = DARK_SECONDARY if dark else MID_GRAY
    focus_color = DARK_ACCENT if dark else PRIMARY_BLUE
    bg_color = DARK_CARD if dark else WHITE
    text_color = DARK_TEXT if dark else DARK_GRAY

    st.markdown(
        f"""
        <style>
        input, textarea, select {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
            border-radius: 8px !important;
            border: 1px solid {border_color} !important;
            padding: 0.5em !important;
            transition: 0.3s;
        }}
        input:focus, textarea:focus, select:focus {{
            border-color: {focus_color} !important;
            box-shadow: 0 0 0 2px rgba(0,120,255,0.3);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_headings(dark=False):
    """Set heading colors and text hierarchy."""
    title_color = DARK_ACCENT if dark else PRIMARY_BLUE
    text_color = DARK_TEXT if dark else DARK_GRAY
    sub_color = DARK_SECONDARY if dark else MID_GRAY

    st.markdown(
        f"""
        <style>
        h1, h2, h3 {{
            color: {title_color};
            font-weight: 700;
        }}
        p {{
            color: {text_color};
        }}
        small, span {{
            color: {sub_color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_cards(dark=False):
    """Add soft shadowed cards for content sections."""
    card_bg = DARK_CARD if dark else WHITE
    shadow = "rgba(0,0,0,0.4)" if dark else "rgba(0,0,0,0.1)"
    st.markdown(
        f"""
        <style>
        .stDataFrame, .stTable {{
            border-radius: 12px;
            background-color: {card_bg};
            box-shadow: 0px 2px 6px {shadow};
        }}
        div[data-testid="stVerticalBlock"] {{
            background-color: {card_bg};
            border-radius: 12px;
            padding: 1.5em;
            margin-bottom: 1em;
            box-shadow: 0 2px 5px {shadow};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_scrollbar(dark=False):
    """Customize scrollbar style."""
    thumb_color = DARK_ACCENT if dark else PRIMARY_BLUE
    st.markdown(
        f"""
        <style>
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        ::-webkit-scrollbar-thumb {{
            background: {thumb_color};
            border-radius: 4px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------
def style_orch(dark_mode=False):
    """Orchestrate all style functions (light or dark mode)."""
    style_layout(dark_mode)
    style_header_footer()
    style_buttons(dark_mode)
    style_sidebar(dark_mode)
    style_inputs(dark_mode)
    style_headings(dark_mode)
    style_cards(dark_mode)
    style_scrollbar(dark_mode)

    import streamlit as st


from ui_style import style_orch

# --- Sidebar toggle for dark mode ---
st.sidebar.title("⚙️ Settings")
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

# Apply styles dynamically
style_orch(dark_mode)

# --- App Header ---
st.title("💙 Streamlit SURA Theme Demo")
st.write("Toggle between light and dark mode to preview the full theme.")

# --- Section: Text Inputs ---
st.subheader("📝 Input Widgets")
col1, col2 = st.columns(2)
with col1:
    st.text_input("Your Name")
    st.text_area("Message")
with col2:
    st.selectbox("Favorite Language", ["Python", "R", "Julia", "C++"])
    st.slider("Experience (years)", 0, 20, 5)

# --- Buttons Section ---
st.subheader("🎛 Buttons & Actions")
c1, c2, c3 = st.columns(3)
c1.button("Primary Action")
c2.download_button("Download", "Sample data...", file_name="data.txt")
c3.form_submit_button("Submit Form")

# --- Data Display ---
import pandas as pd

st.subheader("📊 Data Example")
df = pd.DataFrame(
    {
        "Employee": ["Ana", "Luis", "Sofía", "Carlos"],
        "Department": ["IT", "HR", "Finance", "Marketing"],
        "Score": [88, 92, 85, 90],
    }
)
st.dataframe(df)

# --- Form Example ---
st.subheader("🧾 Contact Form")
with st.form("contact_form"):
    st.text_input("Full Name")
    st.text_input("Email Address")
    st.text_area("Message")
    if st.form_submit_button("Send Message"):
        st.success("✅ Message sent!")

# --- Card-like Section ---
st.subheader("📦 Info Card Example")
with st.container():
    st.markdown("### About This Theme")
    st.markdown(
        "This app demonstrates a **custom UI system** in Streamlit with a SURA-inspired light theme and a dark variant."
    )
    st.button("Learn More")

# --- Footer ---
st.markdown("---")
st.caption("© 2025 - Streamlit Custom Theme Demo | Toggle light/dark mode in sidebar.")
