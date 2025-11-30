import streamlit as st
from streamlit_option_menu import option_menu
from utils.ui_style import *
import time


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


def fixed_header(nombre_usuario: str, gravedad: str, ciudad: str):
    """Display a custom header with user information."""
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
                Usuario: <b>{nombre_usuario}</b> &nbsp;|&nbsp;
                Ciudad: <b>{ciudad}</b> &nbsp;|&nbsp;
                Gravedad: <b style="color:#FFEB3B;">{gravedad}</b>
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


def identification_form(ID_TYPES, SEXO_OPTIONS, DEPARTAMENTOS_CIUDADES):
    """
    Render the patient identification form for the triage process.

    This form collects patient information such as document type, document number,
    sex, department, and city. It reacts dynamically to department selection
    by updating the available city list in real time.

    The function manages and stores values directly into `st.session_state` using
    widget keys, and sets a completion flag (`form_inicio_completed = True`)
    when the form is successfully submitted.

    Parameters
    ----------
    ID_TYPES : list
        List of valid identification document types (e.g., ["Cédula (CC)", "Pasaporte (PA)"]).
    SEXO_OPTIONS : list
        List of valid biological sex options (e.g., ["Masculino", "Femenino"]).
    DEPARTAMENTOS_CIUDADES : dict
        Dictionary mapping each department to its list of available cities.

    Returns
    -------
    None
        Updates `st.session_state` with all entered values and a completion flag.
    """

    # Initialize selected department if not present
    if "selected_departamento" not in st.session_state:
        st.session_state.selected_departamento = list(DEPARTAMENTOS_CIUDADES.keys())[0]

    # ------------- FORM LAYOUT -------------
    col1, col2 = st.columns(2)

    # -------- LEFT COLUMN --------
    with col1:
        tipo_documento = st.selectbox(
            "Tipo de Documento *",
            options=ID_TYPES,
            index=0,
            help="Seleccione el tipo de documento de identificación",
        )

        numero_documento = st.text_input(
            "Número de Documento *",
            placeholder="Ej: 1234567890",
            help="Ingrese el número de documento sin puntos ni espacios",
        )

        sexo = st.selectbox(
            "Sexo Biológico *",
            options=SEXO_OPTIONS,
            help="Seleccione el sexo biológico del paciente",
            key="sexo",
        )

    # -------- RIGHT COLUMN --------
    with col2:
        ## Select departament
        # If no departament is selected, set the first one by default
        # If a departament is already selected, keep it
        departamento = st.selectbox(
            "Departamento *",
            options=list(DEPARTAMENTOS_CIUDADES.keys()),
            index=list(DEPARTAMENTOS_CIUDADES.keys()).index(
                st.session_state.selected_departamento
            ),
            help="Seleccione el departamento de residencia",
            key="departamento_select",
        )

        # Detect department change and refresh the app to update city options
        if departamento != st.session_state.selected_departamento:
            st.session_state.selected_departamento = departamento
            st.session_state.ciudad_selected = ""  # Reset city selection
            st.rerun()

        ciudades_disponibles = DEPARTAMENTOS_CIUDADES[
            st.session_state.selected_departamento
        ]

        ## Select city
        # If no city is selected, set the first one by default
        # If a city is already selected, keep it
        ciudad = st.selectbox(
            "Ciudad/Municipio *",
            options=ciudades_disponibles,
            index=0
            if "ciudad_selected" not in st.session_state
            or not st.session_state.ciudad_selected
            else ciudades_disponibles.index(st.session_state.ciudad_selected),
            help="Seleccione la ciudad o municipio de residencia",
            key="ciudad_selected",
        )

    if st.session_state.get("form_inicio_completed", False):
        st.success("✅ Usuario identificado correctamente")
        st.markdown("")

    # ------------- ACTION BUTTON -------------
    st.markdown("")
    central_col = st.columns([3, 4, 3])[1]
    with central_col:
        submit_button = st.button("🔍 Consultar Usuario", use_container_width=True)

    # ------------- FORM VALIDATION -------------
    if submit_button:
        numero_limpio = numero_documento.strip().replace(" ", "").replace("-", "")

        if not numero_limpio:
            st.error("⚠️ Por favor ingrese el número de documento")
        elif not numero_limpio.isalnum():
            st.error("⚠️ El número de documento contiene caracteres no válidos")
        else:
            # Format document abbreviation (e.g., CC-12345)
            tipo_doc_abrev = (
                tipo_documento.split("(")[1].replace(")", "")
                if "(" in tipo_documento
                else tipo_documento[:2].upper()
            )
            st.session_state.identificacion_paciente = (
                f"{tipo_doc_abrev}-{numero_documento}"
            )

            # Persist selections
            st.session_state.departamento = departamento
            st.session_state.ciudad = ciudad

            # Simulate database check
            with st.spinner("🔍 Consultando base de datos del paciente..."):
                time.sleep(2)

            st.session_state.form_inicio_completed = True
            st.rerun()
