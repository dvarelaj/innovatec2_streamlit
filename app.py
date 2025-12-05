import streamlit as st
import time

from utils.ui_style import general_style_orch
from utils.ui_blocks import (
    menu,
    fixed_header,
    options_navigation_horizontal,
    identification_form,
    symptoms_form,
    display_triage_result,
)
from utils.input_data.triage_symptoms import get_triage_decision
from utils.ui_maps import map_triage_locate
from utils.ui_data import (
    ID_TYPES,
    SEXO_OPTIONS,
    get_departamentos_ciudades_from_providers,
)
from utils.ui_geocode import (
    # get_coordinates_co,
    # reverse_geocode,
    geocode_address_arcgis,
    reverse_geocode_arcgis,
)


# -------------------------------------------------------------------------
## Inicialización de variables de estado


# Inicializa el estado de la pestaña de la pagina de inicio
if "current_tab_triage" not in st.session_state:
    st.session_state.current_tab_triage = "Inicio"

# Datos del paciente del estado de la sesión
identificacion_paciente = st.session_state.get("identificacion_paciente", "")
decision = st.session_state.get("decision", "")
ciudad = st.session_state.get("ciudad", "")

# Variables del usuario
tipo_documento = st.session_state.get("tipo_documento", "")
numero_documento = st.session_state.get("numero_documento", "")
sexo = st.session_state.get("sexo", "")
departamento = st.session_state.get("departamento", "")

# Variables de las preguntas tipo Triage
for key in [
    "selected_categoria",
    "selected_sintoma",
    "selected_modificador",
    "form_symptoms_completed",
]:
    if key not in st.session_state:
        st.session_state[key] = None

# Variables de decisiones del triage
for key in [
    "decision_triage",
    "decision_modalidad",
    "decision_especialidad",
]:
    if key not in st.session_state:
        st.session_state[key] = None

# Variables para sistema de recomendación
if "recommendation_step" not in st.session_state:
    st.session_state.recommendation_step = False
if "recommended_providers" not in st.session_state:
    st.session_state.recommended_providers = None

# Variables para ubicación en mapas (Triage)
for key in [
    "coordinates_queried_ciudad",
    "last_processed_click",
    "last_auto_location",
    "last_geocoded_key",
    "form_location_completed",
]:
    if key not in st.session_state:
        st.session_state[key] = None

ubicacion_usuario = st.session_state.get("ubicacion_usuario", None)

# Variables de finalización del triage y preparación siguiente paso
for key in ["triage_completed"]:
    if key not in st.session_state:
        st.session_state[key] = None


# -------------------------------------------------------------------------
## Inicialización de estilos y componentes

general_style_orch()  # Inject custom styles
menu()  # Setup sidebar menu
fixed_header(
    identificacion_paciente,
    decision,
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

# Cargar ubicaciones dinámicamente desde datos de proveedores
with st.spinner("🔄 Cargando directorio de proveedores"):
    DEPARTAMENTOS_CIUDADES = get_departamentos_ciudades_from_providers()

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

        # Obtener la decisión del triage basada en los síntomas seleccionados
        if valid_symptoms:
            if st.session_state.get("decision_triage", None):
                # ------------
                ## Actualizar la decisión basada en el triage

                # si es T1 o T2 -> Emergencia
                if (st.session_state.decision_triage == "T1") | (
                    st.session_state.decision_triage == "T2"
                ):
                    st.session_state.decision = "Emergencia"
                # si es T3 -> Urgencias
                elif st.session_state.decision_triage == "T3":
                    st.session_state.decision = "Urgencias"
                # si es T4 -> Cita Prioritaria
                elif st.session_state.decision_triage == "T4":
                    st.session_state.decision = "Cita Prioritaria"
                # si es T5 -> Cita Programada
                elif st.session_state.decision_triage == "T5":
                    st.session_state.decision = "Cita Programada"

            # ------------
            # Mostrar información del resultado del triage
            display_triage_result()

            st.markdown("---")

            if st.session_state.get("form_symptoms_completed", False):
                st.success(
                    "✅ **Síntomas registrados correctamente.** "
                    "A continuación, especifique su ubicación exacta para completar el triage."
                )

        else:
            if all(
                [
                    st.session_state.get("selected_categoria"),
                    st.session_state.get("selected_sintoma"),
                    st.session_state.get("selected_modificador"),
                ]
            ):
                st.markdown("---")
                st.error("❌ **Combinación inválida. Revise su selección.**")

        #  Navegación de regreso a pestaña de identificación
        cols = st.columns([2, 4, 2])
        with cols[0]:
            if st.button("← Volver al Inicio", use_container_width=True):
                st.session_state.current_tab_triage = "Inicio"
                st.rerun()

        # Navegación a pestaña de Mapa ubicación
        if valid_symptoms:
            with cols[2]:
                if st.button("Ubicación →", use_container_width=True):
                    st.session_state.current_tab_triage = "Mapa ubicación"
                    st.rerun()

    else:
        st.warning(
            "⚠️ Por favor complete primero la sección de Identificación del usuario."
        )

elif selected == "Mapa ubicación":
    # --------------------------
    ## Sección de ubicación del usuario y Mapa ubicación

    if st.session_state.get("form_inicio_completed", False):
        st.markdown("### Ubicación del Usuario")

        # Metodos para ubicar al usuario
        modo_ubi = st.radio(
            "Seleccione el metodo para ubicar su posición:",
            options=[
                "Selección manual",
                "Ubicación del dispositivo",
                "Escribir dirección",
            ],
            index=0,
            key="map_location_option",
            horizontal=True,
        )

        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

        # ------------
        ## Seleccionar ubicación en el mapa manualmente
        if modo_ubi == "Selección manual":
            st.markdown("📍 **Haz clic en el mapa para seleccionar tu ubicación**")

            center_column = st.columns([1, 8, 1])[1]
            with center_column:
                map_output = map_triage_locate(
                    ubicacion_usuario, modo_ubicacion="Manual"
                )

            # -----------
            # Detectar nuevos clics y actualizar el marcador
            if map_output and map_output["last_clicked"]:
                new_location = map_output["last_clicked"]
                # Comprueba si se trata de un clic NUEVO (diferente de la ubicación almacenada anteriormente).
                last_processed = st.session_state.get("last_processed_click")
                if last_processed != new_location:
                    # Este es un nuevo clic - procesarlo
                    st.session_state["ubicacion_usuario"] = new_location
                    st.session_state["last_processed_click"] = new_location
                    st.rerun()  # Volver a ejecutar la app para actualizar el marcador

        # ------------
        ## Seleccionar ubicación en el mapa de manera automatica via plugins
        elif modo_ubi == "Ubicación del dispositivo":
            center_column = st.columns([1, 8, 1])[1]
            with center_column:
                map_output = map_triage_locate(ubicacion_usuario, modo_ubicacion="Auto")

            # Capturar la ubicación del centro del mapa (localizacion automática)
            if map_output and map_output.get("center"):
                auto_location = {
                    "lat": map_output["center"]["lat"],
                    "lng": map_output["center"]["lng"],
                }

                # Verificar si es una nueva ubicación detectada automáticamente
                last_auto = st.session_state.get("last_auto_location")

                if last_auto != auto_location and auto_location != {
                    "lat": st.session_state.get("city_lat"),
                    "lng": st.session_state.get("city_lon"),
                }:
                    # Nueva ubicación automática detectada
                    st.session_state["ubicacion_usuario"] = auto_location
                    st.session_state["last_auto_location"] = auto_location
                    st.rerun()

        # ------------
        ## Ingresar dirección manualmente para geocodificar
        elif modo_ubi == "Escribir dirección":
            # Formulario para ingresar dirección manualmente
            with st.form("address_form"):
                address_input = st.text_input(
                    "Ingrese la dirección lo mas completa posible:",
                    placeholder="Ej: Carrera 7 #32-16, Chapinero, Bogotá, Cundinamarca",
                )
                submit_address = st.form_submit_button("🔍 Buscar Ubicación")

            if submit_address and address_input:
                with st.spinner("Buscando ubicación..."):
                    # Geocodificar la dirección usando ArcGIS
                    result = geocode_address_arcgis(address_input)

                    if result:
                        # Actualizar la ubicación del usuario
                        st.session_state["ubicacion_usuario"] = {
                            "lat": result["lat"],
                            "lng": result["lng"],
                        }
                        st.rerun()
                    else:
                        st.error(
                            "❌ No se pudo encontrar la dirección. Por favor, intente con otra dirección más específica."
                        )

            # Mostrar el mapa con la ubicación geocodificada
            if ubicacion_usuario:
                center_column = st.columns([1, 8, 1])[1]
                with center_column:
                    map_output = map_triage_locate(
                        ubicacion_usuario, modo_ubicacion="Manual"
                    )

                    # -----------
                # Detectar nuevos clics y actualizar el marcador
                if map_output and map_output["last_clicked"]:
                    new_location = map_output["last_clicked"]
                    # Comprueba si se trata de un clic NUEVO (diferente de la ubicación almacenada anteriormente).
                    last_processed = st.session_state.get("last_processed_click")
                    if last_processed != new_location:
                        # Este es un nuevo clic - procesarlo
                        st.session_state["ubicacion_usuario"] = new_location
                        st.session_state["last_processed_click"] = new_location
                        st.rerun()  # Volver a ejecutar la app para actualizar el marcador

        # ------------
        ## Obtener la direccion a partir de la latitud y longitud del usuario
        if ubicacion_usuario:
            lat = ubicacion_usuario["lat"]
            lon = ubicacion_usuario["lng"]

            # Crear una clave única para esta ubicación
            location_key = f"{lat:.6f}_{lon:.6f}"

            # Solo llamar a reverse_geocode si la ubicación cambió
            if st.session_state.get("last_geocoded_key") != location_key:
                address = reverse_geocode_arcgis(lat, lon)
                st.session_state["cached_address"] = address
                st.session_state["last_geocoded_key"] = location_key
            else:
                # Usar la dirección en caché
                address = st.session_state.get("cached_address", "Cargando...")

            # Mostrar la dirección obtenida
            st.success(f"**Dirección aproximada**: {address}")

            # Checkbox para confirmar la ubicación
            col_center = st.columns([3, 4, 3])[1]
            with col_center:
                st.markdown(
                    """
                    <style>
                    div[data-testid="stCheckbox"] label p {
                        font-size: 1.1rem !important;
                        font-weight: 600 !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                location_confirmed = st.checkbox(
                    "¿Está de acuerdo con esta ubicación?",
                    key="location_confirmation_checkbox",
                )

            # Actualizar variable de sesión cuando se confirma
            if location_confirmed:
                st.session_state["form_location_completed"] = True
            else:
                st.session_state["form_location_completed"] = False

        # Navegación de regreso a pestaña de formulario
        arrow_cols = st.columns([2, 4, 2])
        with arrow_cols[0]:
            if st.button("← Volver al Formulario", use_container_width=True):
                st.session_state.current_tab_triage = "Formulario"
                st.rerun()

        # --------------
        # Validar si se completó todo el triage para habilitar el botón de finalizar
        st.session_state.triage_completed = all(
            [
                st.session_state["form_inicio_completed"],
                st.session_state["form_symptoms_completed"],
                st.session_state["form_location_completed"],
            ]
        )

        if st.session_state.get("triage_completed", False):
            with arrow_cols[2]:
                if st.button("Seguir a Recomendación →", use_container_width=True):
                    st.session_state.recommendation_step = True
                    st.switch_page("pages/2_recomendacion.py")

        if st.session_state.get("triage_completed", False):
            st.info(
                "✅ **El formulario de triage ha sido completado con éxito.** Haga clic en 'Seguir a Recomendación' para ver los prestadores sugeridos."
            )

    else:
        st.warning(
            "⚠️ Por favor complete primero la sección de Identificación del Usuario."
        )
