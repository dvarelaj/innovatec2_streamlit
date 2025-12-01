import streamlit as st
import time

from utils.ui_style import general_style_orch
from utils.ui_blocks import (
    menu,
    fixed_header,
    options_navigation_horizontal,
    identification_form,
    symptoms_form,
)
from utils.ui_maps import map_triage_locate
from utils.ui_data import ID_TYPES, SEXO_OPTIONS, DEPARTAMENTOS_CIUDADES


# -------------------------------------------------------------------------
## Inicialización de variables de estado


# Inicializa el estado de la pestaña de la pagina de inicio
if "current_tab_triage" not in st.session_state:
    st.session_state.current_tab_triage = "Inicio"

# Datos del paciente del estado de la sesión
identificacion_paciente = st.session_state.get("identificacion_paciente", "")
gravedad = st.session_state.get("gravedad", "")
ciudad = st.session_state.get("ciudad", "")

# Variables del usuario
tipo_documento = st.session_state.get("tipo_documento", "")
numero_documento = st.session_state.get("numero_documento", "")
sexo = st.session_state.get("sexo", "")
departamento = st.session_state.get("departamento", "")

# Variables de las preguntas tipo Triage
for key in ["selected_categoria", "selected_sintoma", "selected_modificador"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Variables para ubicación en mapas
for key in ["coordinates_queried_ciudad"]:
    if key not in st.session_state:
        st.session_state[key] = None

ubicacion_usuario = st.session_state.get("ubicacion_usuario", None)


# -------------------------------------------------------------------------
## Inicialización de estilos y componentes

general_style_orch()  # Inject custom styles
menu()  # Setup sidebar menu
fixed_header(
    identificacion_paciente,
    gravedad,
    ciudad,
)  # Custom fixed header


# -------------------------------------------------------------------------
## Navegación de pestañas horizontal - pagina triage

st.markdown(" ___ ")

# Barra de navegación superior
selected = options_navigation_horizontal(
    st.session_state.current_tab_triage,
)

# Actualiza la pestaña actual al hacer clic
st.session_state.current_tab_triage = selected

if selected == "Inicio":
    # --------------------------
    ## Sección de inicio y formulario de identificación del usuario

    st.markdown("### Identificación del Usuario")
    st.markdown("Complete los siguientes datos para iniciar el proceso de triage.")
    st.markdown("")

    # Inicializar estado de formulario completado
    if "form_inicio_completed" not in st.session_state:
        st.session_state.form_inicio_completed = False

    # ------------------------
    ## Formulario de identificación del usuario
    identification_form(ID_TYPES, SEXO_OPTIONS, DEPARTAMENTOS_CIUDADES)

elif selected == "Formulario":
    # --------------------------
    ## Sección de formulario de triage de síntomas

    if st.session_state.get("form_inicio_completed", False):
        st.markdown("### Selección de Síntomas")

        # --------------------------
        ## Formulario de preguntas tipo triage
        valid_symptoms = symptoms_form()

        #  Navegación de regreso a pestaña de identificación
        cols = st.columns([2, 4, 2])
        with cols[0]:
            if st.button("⬅️ Volver al Inicio", use_container_width=True):
                st.session_state.current_tab_triage = "Inicio"
                st.rerun()

        # Navegación a pestaña de mapa interactivo
        if valid_symptoms:
            with cols[2]:
                if st.button("Ubicación ➡️", use_container_width=True):
                    st.session_state.current_tab_triage = "Mapa Interactivo"
                    st.rerun()
    else:
        st.warning(
            "⚠️ Por favor complete primero la sección de Identificación del usuario."
        )

elif selected == "Mapa Interactivo":
    # --------------------------
    ## Sección de ubicación del usuario y mapa Interactivo

    if st.session_state.get("form_inicio_completed", False):
        st.markdown("### Ubicación del Usuario")

        modo_ubi = st.radio(
            "Seleccione el metodo para ubicar su posición:",
            options=[
                "Hacer clic en el mapa",
                "Usar ubicación actual del dispositivo",
                "Escribir dirección",
            ],
            index=0,
            key="map_location_option",
            horizontal=True,
        )

        center_column = st.columns([1, 8, 1])[1]
        with center_column:
            map_output = map_triage_locate(ubicacion_usuario)

        # --- Detect new clicks and update marker ---
        if map_output and map_output["last_clicked"]:
            st.session_state["user_location"] = map_output["last_clicked"]
            st.rerun()  # refresh map to show new marker immediately

        if ubicacion_usuario:
            lat = ubicacion_usuario["lat"]
            lon = ubicacion_usuario["lng"]
            col_center = st.columns([3, 4, 4])[1]
            with col_center:
                st.success(f"📍 Ubicación seleccionada: ({lat:.4f}, {lon:.4f})")
        else:
            st.info("Haz clic en el mapa para seleccionar tu ubicación.")

        cols = st.columns([2, 4, 2])
        with cols[0]:
            if st.button("⬅️ Volver al Formulario", use_container_width=True):
                st.session_state.current_tab_triage = "Formulario"
                st.rerun()
        with cols[2]:
            if st.button("Finalizar formulario", use_container_width=True):
                st.session_state.triage_completed = True

        if st.session_state.get("triage_completed", False):
            st.success("✅ El formulario de triage ha sido completado con éxito.")

    else:
        st.warning(
            "⚠️ Por favor complete primero la sección de Identificación del Usuario."
        )

st.markdown("___")

# st.markdown(
#     """
# <div style="
#     background-color:#e8f5e9;
#     padding:15px;
#     border-radius:10px;
#     border:1px solid #a5d6a7;
#     text-align:center;">
#     <h3 style='color:#2e7d32;'>✅ Recomendación</h3>
#     <p>El centro médico <b>Clínica del Norte</b> está a solo <b>2.1 km</b>.</p>
# </div>
# """,
#     unsafe_allow_html=True,
# )
