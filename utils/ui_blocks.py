import streamlit as st
from streamlit_option_menu import option_menu
from utils.ui_style import *
from utils.input_data.triage_symptoms import (
    get_categorias,
    get_sintomas,
    get_modificadores,
    validate_selection,
    get_triage_decision,
)
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
    # st.sidebar.page_link("pages/1_styles_test.py", label="Style Test Page")

    hide_menu_style = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.sidebar.markdown("---")


def fixed_header(nombre_usuario: str, decision: str, ciudad: str):
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
                Decisión: <b style="color:#FFEB3B;">{decision}</b>
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
    ("Inicio", "Formulario", "Mapa ubicación") styled according to the provided
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
        The name of the selected option ("Inicio", "Formulario", or "Mapa ubicación").
    """

    selected = option_menu(
        menu_title=None,
        options=["Inicio", "Formulario", "Mapa ubicación"],
        icons=["house", "file-earmark-text", "map"],
        orientation="horizontal",
        default_index=["Inicio", "Formulario", "Mapa ubicación"].index(current_tab),
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

    # Initialize session state variables
    if "selected_departamento" not in st.session_state:
        st.session_state.selected_departamento = ""
    if "ciudad_selected" not in st.session_state:
        st.session_state.ciudad_selected = ""

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
            options=[""] + SEXO_OPTIONS,
            help="Seleccione el sexo biológico del usuario",
            key="sexo",
        )

    # -------- RIGHT COLUMN --------
    with col2:
        ## Select departamento (con opción vacía inicial)
        all_departamentos = [""] + list(DEPARTAMENTOS_CIUDADES.keys())

        departamento_index = (
            0
            if not st.session_state.selected_departamento
            else all_departamentos.index(st.session_state.selected_departamento)
        )

        departamento = st.selectbox(
            "Departamento",
            options=all_departamentos,
            index=departamento_index,
            help="Seleccione el departamento o déjelo vacío para ver todas las ciudades",
            key="departamento_select",
        )

        # Detect department change and update session state
        if departamento != st.session_state.selected_departamento:
            st.session_state.selected_departamento = departamento
            # Si cambia el departamento, resetear la ciudad solo si hay un departamento seleccionado
            if departamento:
                st.session_state.ciudad_selected = ""
            st.rerun()

        ## Select city - mostrar todas las ciudades o filtrar por departamento
        if st.session_state.selected_departamento:
            # Si hay departamento seleccionado, mostrar solo ciudades de ese departamento
            ciudades_disponibles = DEPARTAMENTOS_CIUDADES[
                st.session_state.selected_departamento
            ]
        else:
            # Si no hay departamento, mostrar TODAS las ciudades
            ciudades_disponibles = sorted(
                set(
                    ciudad
                    for ciudades in DEPARTAMENTOS_CIUDADES.values()
                    for ciudad in ciudades
                )
            )

        # Añadir opción vacía al inicio
        ciudades_con_vacio = [""] + ciudades_disponibles

        ciudad_index = (
            0
            if not st.session_state.ciudad_selected
            or st.session_state.ciudad_selected not in ciudades_disponibles
            else ciudades_con_vacio.index(st.session_state.ciudad_selected)
        )

        ciudad = st.selectbox(
            "Ciudad/Municipio *",
            options=ciudades_con_vacio,
            index=ciudad_index,
            help="Seleccione la ciudad o municipio",
            key="ciudad_selected_widget",
        )

        # Actualizar session state con la ciudad seleccionada
        if ciudad != st.session_state.ciudad_selected:
            st.session_state.ciudad_selected = ciudad

    # ------------- FORM RESPONSE -------------
    if st.session_state.get("form_inicio_completed", False):
        st.success("✅ Usuario identificado correctamente")
        st.markdown("")

        arrow_cols = st.columns([3, 4, 3])
        with arrow_cols[1]:
            if st.button("Seguir al Formulario →", use_container_width=True):
                st.session_state.current_tab_triage = "Formulario"
                st.rerun()

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
        elif not ciudad:
            st.error("⚠️ Por favor seleccione una ciudad o municipio")
        elif not sexo:
            st.error("⚠️ Por favor seleccione el sexo biológico")
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

            # Persist selections (si no hay departamento, guardarlo como vacío)
            st.session_state.departamento = departamento if departamento else ""
            st.session_state.ciudad = ciudad

            # Simulate database check
            with st.spinner("🔍 Consultando base de datos del paciente..."):
                time.sleep(3)

            st.session_state.form_inicio_completed = True
            st.rerun()


def symptoms_form(
    get_categorias=get_categorias,
    get_sintomas=get_sintomas,
    get_modificadores=get_modificadores,
    validate_selection=validate_selection,
):
    """
    Render the triage symptom selection form in Streamlit.

    This form guides the user through a 3-step symptom identification process:
    - Selecting the body area (category)
    - Selecting the specific symptom within that category
    - Selecting a symptom modifier (if applicable)

    All selections are stored in `st.session_state`. The function also validates
    the final combination of category, symptom, and modifier using the provided
    `validate_selection()` function.

    Parameters
    ----------
    get_categorias : function
        A function that returns a list of available body categories.
    get_sintomas : function
        A function that receives a category and returns a list of symptoms related to it.
    get_modificadores : function
        A function that receives (category, symptom) and returns a list of possible modifiers.
    validate_selection : function
        A function that receives (category, symptom, modifier) and returns True if
        the combination is valid, otherwise False.

    Returns
    -------
    bool
        True if a valid combination of category, symptom, and modifier is selected.
        False otherwise.
    """

    try:
        # ---------  CATEGORIES ----------------
        categorias = get_categorias()

        # Determine index dynamically to preserve user's previous selection
        categoria_index = (
            0
            if not st.session_state.get("selected_categoria")
            else categorias.index(st.session_state.selected_categoria) + 1
        )

        categoria = st.selectbox(
            "1️⃣ ¿En qué área del cuerpo se presenta el síntoma? *",
            options=["Seleccione una opción..."] + categorias,
            index=categoria_index,
            help="Seleccione la categoría que mejor describe el área afectada",
            key="categoria_select",
        )

        # Update the selected category in session_state
        if categoria != "Seleccione una opción...":
            st.session_state.selected_categoria = categoria
        else:
            # Reset downstream selections if user resets category
            st.session_state.selected_categoria = None
            st.session_state.selected_sintoma = None
            st.session_state.selected_modificador = None

        # ------------  SYMPTOMS --------------
        # Select Symptom (only shown if category is selected)
        if st.session_state.selected_categoria:
            sintomas = get_sintomas(st.session_state.selected_categoria)

            # Determine index dynamically to preserve user's previous selection
            sintoma_index = (
                0
                if not st.session_state.get("selected_sintoma")
                else sintomas.index(st.session_state.selected_sintoma) + 1
            )

            sintoma = st.selectbox(
                "2️⃣ ¿Cuál de los siguientes síntomas te identifica mejor? *",
                options=["Seleccione una opción..."] + sintomas,
                index=sintoma_index,
                help="Seleccione el síntoma específico que presenta",
                key="sintoma_select",
            )

            if sintoma != "Seleccione una opción...":
                st.session_state.selected_sintoma = sintoma
            else:
                # Reset next step if symptom is deselected
                st.session_state.selected_sintoma = None
                st.session_state.selected_modificador = None

        # ------------  MODIFIERS --------------
        # Select Modifier (only shown if symptom is selected)
        if st.session_state.get("selected_sintoma"):
            modificadores = get_modificadores(
                st.session_state.selected_categoria, st.session_state.selected_sintoma
            )

            # Determine index dynamically to preserve user's previous selection
            modificador_index = (
                0
                if not st.session_state.get("selected_modificador")
                else modificadores.index(st.session_state.selected_modificador) + 1
            )

            modificador = st.selectbox(
                "3️⃣ ¿El síntoma está asociado con alguna de estas características? *",
                options=["Seleccione una opción..."] + modificadores,
                index=modificador_index,
                help="Seleccione el modificador que mejor describe su situación",
                key="modificador_select",
            )

            if modificador != "Seleccione una opción...":
                st.session_state.selected_modificador = modificador
            else:
                st.session_state.selected_modificador = None

        # ------------  VALIDATION TRIAGE  --------------
        # Validate full selection
        if all(
            [
                st.session_state.get("selected_categoria"),
                st.session_state.get("selected_sintoma"),
                st.session_state.get("selected_modificador"),
            ]
        ):
            is_valid = validate_selection(
                st.session_state.selected_categoria,
                st.session_state.selected_sintoma,
                st.session_state.selected_modificador,
            )

            if is_valid:
                st.session_state["form_symptoms_completed"] = True

                # ------------  TRIAGE RESULTS  --------------
                # Get triage decision
                triage_decision = get_triage_decision(
                    st.session_state.selected_categoria,
                    st.session_state.selected_sintoma,
                    st.session_state.selected_modificador,
                )
                st.session_state["decision_triage"] = triage_decision["triage"]
                st.session_state["decision_modalidad"] = triage_decision["modalidad"]
                st.session_state["decision_especialidad"] = triage_decision[
                    "especialidad"
                ]

                return True
            else:
                st.session_state["form_symptoms_completed"] = False
                return False

        # If not all selections are complete, return False by default
        return False

    except Exception:
        # Reset selections on error
        st.session_state.selected_categoria = None
        st.session_state.selected_sintoma = None
        st.session_state.selected_modificador = None

        st.rerun()

        return False


def display_triage_result():
    """
    Display the triage result panel in the Streamlit UI.

    This function renders a collapsible section summarizing the triage decision,
    including the classification (triage level, modality, and severity),
    the recommended medical specialty, and next steps for the user.

    It reads data directly from Streamlit's session state:
        - decision_triage
        - decision
        - decision_modalidad
        - decision_especialidad

    The visual presentation adapts color, icon, and message
    depending on the triage level (T1–T5).

    Example
    -------
    >>> display_triage_result()
    """

    with st.expander("ℹ️ Resultado del Triage", expanded=False):
        # --- Layout: Two columns ---
        cols = st.columns([4, 1, 4])

        # ===========================
        # 🔹 Column 1: Classification
        # ===========================
        with cols[0]:
            st.markdown("#### Clasificación")

            # Retrieve triage info from session state
            nivel = st.session_state.get("decision_triage", "N/A")
            decision = st.session_state.get("decision", "N/A")

            # Define color and icon by severity level
            if nivel in ["T1", "T2"]:
                color = "#D32F2F"  # Red - Emergency
                emoji = "🚨"
            elif nivel == "T3":
                color = "#F57C00"  # Orange - Urgent
                emoji = "⚠️"
            elif nivel == "T4":
                color = "#FBC02D"  # Yellow - Priority
                emoji = "⏱️"
            else:  # T5 or undefined
                color = "#388E3C"  # Green - Regular
                emoji = "✅"

            # Render colored triage label
            st.markdown(
                f"""
                <div style="
                    background-color: {color};
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 1.2rem;
                ">
                    {emoji} Nivel {nivel} - {decision}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Add modality
            st.markdown("")
            st.write(
                f"**Modalidad:** {st.session_state.get('decision_modalidad', 'N/A')}"
            )

        # ===========================
        # 🔹 Column 2: Recommendation
        # ===========================
        with cols[2]:
            st.markdown("#### Recomendación")
            especialidad = st.session_state.get("decision_especialidad", "N/A")
            if especialidad != "N/A":
                especialidad = especialidad.replace("_", " ").capitalize()
            st.write(f"**Especialidad requerida:** {especialidad}")
            st.markdown("")

            # Display contextual guidance message
            if nivel in ["T1", "T2"]:
                st.error(
                    "⚠️ **Atención inmediata requerida**\n\n"
                    "Diríjase a la sala de urgencias más cercana o llame al ***."
                )
            elif nivel == "T3":
                st.warning(
                    "📍 **Atención urgente**\n\n"
                    "Debe acudir a urgencias lo antes posible."
                )
            elif nivel == "T4":
                st.info(
                    "📅 **Cita prioritaria**\n\n"
                    "Se recomienda agendar una cita médica prioritaria (<48 horas)."
                )
            else:  # T5
                st.success(
                    "📆 **Cita programada**\n\n"
                    "Puede agendar una cita médica de manera regular por nuestro sistema."
                )

        # ===========================
        # 🔹 Footer: Next Steps
        # ===========================
        st.markdown("---")
        st.markdown("#### 📍 Próximos pasos")
        st.write(
            "1. Complete la información de su ubicación en la siguiente pestaña\n"
            "2. Obtenga recomendaciones de prestadores cercanos"
        )


###################
# RECOMMENDATION UI BLOCKS #
###################


def options_navigation_recomendacion(
    current_tab: str,
    PRIMARY_BLUE: str = PRIMARY_BLUE,
    LIGHT_BLUE: str = LIGHT_BLUE,
    DARK_GRAY: str = DARK_GRAY,
    WHITE: str = WHITE,
) -> str:
    """
    Create a horizontal navigation bar for 'Resumen' and 'Ruta' using `streamlit-option-menu`.

    Parameters
    ----------
    current_tab : str
        The currently active tab name (should be either "Resumen" or "Ruta").
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
        The name of the selected option ("Resumen" or "Ruta").
    """

    options = ["Resumen", "Ruta"]
    icons = ["list-ul", "map"]

    selected = option_menu(
        menu_title=None,
        options=options,
        icons=icons,
        orientation="horizontal",
        default_index=options.index(current_tab),
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
