import streamlit as st
import numpy as np
import pandas as pd
from streamlit_folium import st_folium

import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, Draw, MeasureControl

from utils.ui_style import general_style_orch
from utils.ui_blocks import menu, fixed_header, options_navigation_horizontal
from utils.ui_maps import map_triage_locate

# -------------------------------------------------------------------------
## Inicialización de variables de estado


# Inicializa el estado de la pestaña de la pagina de inicio
if "current_tab_triage" not in st.session_state:
    st.session_state.current_tab_triage = "Inicio"

# Datos del paciente del estado de la sesión
identificacion = st.session_state.get("identificacion_paciente", "")
gravedad = st.session_state.get("gravedad", "")
ciudad = st.session_state.get("ciudad", "")

# Variables del triage
ubicacion_usuario = st.session_state.get("user_location", None)

# -------------------------------------------------------------------------
## Inicialización de estilos y componentes

general_style_orch()  # Inject custom styles
menu()  # Setup sidebar menu
fixed_header(
    identificacion,
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
    ## Formulario de identificación incial
    st.empty()
    cols = st.columns([2, 8, 2])
    with cols[2]:
        if st.button("Ir al Formulario ➡️"):
            st.session_state.current_tab_triage = "Formulario"
            st.rerun()

elif selected == "Formulario":
    # --------------------------
    ## Formulario de preguntas tipo triage
    st.empty()
    cols = st.columns([2, 4, 1])
    with cols[0]:
        if st.button("⬅️ Volver al Inicio"):
            st.session_state.current_tab_triage = "Inicio"
            st.rerun()
    with cols[2]:
        if st.button("Ir al Mapa ➡️ "):
            st.session_state.current_tab_triage = "Mapa Interactivo"
            st.rerun()

elif selected == "Mapa Interactivo":
    # --------------------------
    ## Sección de mapa Interactivo
    st.markdown("## Ubicación del Paciente")
    st.markdown("Especifica tu ubicación exacta")

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

    cols = st.columns([2, 6, 2])
    with cols[0]:
        if st.button("⬅️ Volver al Formulario"):
            st.session_state.current_tab_triage = "Formulario"
            st.rerun()
    with cols[2]:
        if st.button("Finalizar formulario"):
            st.session_state.triage_completed = True

    if st.session_state.get("triage_completed", False):
        st.success("✅ El formulario de triage ha sido completado con éxito.")

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
