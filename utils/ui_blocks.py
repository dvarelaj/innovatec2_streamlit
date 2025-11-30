import streamlit as st
from streamlit_option_menu import option_menu
from utils.ui_style import *

BUG_REPORT_URL = "https://www.sura.co/arl"
HELP_URL = "https://www.sura.co/arl"
PAGE_TITLE = "ARL"
PAGE_ICON = "🏥"


def menu() -> None:
    """
    Configure and display the sidebar menu for the Streamlit application.

    Returns
    -------
    None
    """
    if "set_page_config" not in st.session_state:
        st.session_state.set_page_config = st.set_page_config(
            page_title=PAGE_TITLE,
            page_icon=PAGE_ICON,
            layout="centered",
            initial_sidebar_state="expanded",
            menu_items={
                "Get Help": HELP_URL,
                "Report a bug": BUG_REPORT_URL,
                "About": PAGE_TITLE,
            },
        )
    st.sidebar.image("assets/logos/temp.png", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.page_link("app.py", label="Triage")
    st.sidebar.page_link("pages/1_styles_test.py", label="Style Test Page")

    hide_menu_style = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.sidebar.markdown("---")


def fixed_header(nombre_paciente: str, gravedad: str, ciudad: str):
    """Display a custom header with patient information."""
    st.markdown(
        f"""
        <style>
        .header {{
            background-color: {SECONDARY_BLUE};
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .info {{
            font-size: 14px;
        }}
        .title {{
            font-size: 22px;
            font-weight: bold;
        }}
        </style>

        <div class="header">
            <div class="title">🏥 RutaSalud - Recomendador de Rutas</div>
            <div class="info">
                Paciente: <b>{nombre_paciente}</b> &nbsp;|&nbsp;
                Gravedad: <b style="color:#FFEB3B;">{gravedad}</b> &nbsp;|&nbsp;
                Ciudad: <b>{ciudad}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def options_navigation_horizontal(
    current_tab: str,
    PRIMARY_BLUE: str = PRIMARY_BLUE,
    LIGHT_BLUE: str = LIGHT_BLUE,
    DARK_GRAY: str = DARK_GRAY,
    WHITE: str = WHITE,
) -> str:
    """
    Create a horizontal navigation bar using `streamlit-option-menu`.

    This component displays a responsive horizontal menu with three main options
    ("Inicio", "Formulario", "Mapa Interactivo") styled according to the provided
    color palette. It is designed to be used as the main navigation header for
    Streamlit multi-section apps.

    Parameters
    ----------
    current_tab : str
        The currently active tab name (to keep selection consistent across reruns).
    PRIMARY_BLUE : str, optional
        Main corporate blue used for selected tab background and borders.
    LIGHT_BLUE : str, optional
        Lighter blue used for hover effects.
    DARK_GRAY : str, optional
        Text color for unselected tabs.
    WHITE : str, optional
        Background color for the navigation container.

    Returns
    -------
    str
        The name of the selected option ("Inicio", "Formulario", or "Mapa Interactivo").
    """

    selected = option_menu(
        menu_title=None,
        options=["Inicio", "Formulario", "Mapa Interactivo"],
        icons=["house", "file-earmark-text", "map"],
        orientation="horizontal",
        default_index=["Inicio", "Formulario", "Mapa Interactivo"].index(current_tab),
        styles={
            "container": {
                "padding": "0!important",
                "background-color": WHITE,
                "border-bottom": f"2px solid {PRIMARY_BLUE}",
            },
            "icon": {"color": PRIMARY_BLUE, "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "font-weight": "500",
                "text-align": "center",
                "margin": "0px",
                "color": DARK_GRAY,
                "--hover-color": LIGHT_BLUE,
                "border-radius": "4px",
            },
            "nav-link-selected": {
                "background-color": LIGHT_BLUE,
                "color": DARK_GRAY,
                "border-radius": "4px",
            },
        },
    )

    return selected
