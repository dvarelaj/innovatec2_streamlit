"""
Página de Recomendación de Prestadores de Salud.

Esta página muestra las recomendaciones de prestadores basadas en el triage
completado, con dos tabs: Resumen y Ruta.
"""

import streamlit as st
from streamlit_option_menu import option_menu
import folium
from streamlit_folium import st_folium
from folium import plugins

from utils.ui_style import general_style_orch
from utils.ui_blocks import menu, fixed_header, options_navigation_recomendacion
from utils.matching_utils.recommendation_engine import (
    build_triage_correspondence_table,
    get_recommended_services,
    filter_providers_by_service_and_location,
    load_and_prepare_provider_data,
)
from utils.general_utils import text_cleaning
from utils.debug_utils import show_recommendation_debug_info


# -------------------------------------------------------------------------
## Inicialización de estilos y componentes

general_style_orch()
menu()

# Variables para el header
identificacion_paciente = st.session_state.get("identificacion_paciente", "")
decision = st.session_state.get("decision", "")
ciudad = st.session_state.get("ciudad", "")

fixed_header(identificacion_paciente, decision, ciudad)

# -------------------------------------------------------------------------
## Verificar que el usuario haya completado el triage

if not st.session_state.get("triage_completed", False):
    st.error("⚠️ Debe completar el proceso de triage antes de acceder a esta página.")
    st.info("👈 Por favor, regrese a la página de inicio para completar el triage.")
    st.stop()

# -------------------------------------------------------------------------
## Título de la página

st.markdown("")
st.markdown("# Recomendación de Prestadores")
st.markdown("___")

# -------------------------------------------------------------------------
## Procesamiento de datos de recomendación

# Inicializar variables de sesión para esta página
if "recommendation_data_loaded" not in st.session_state:
    st.session_state.recommendation_data_loaded = False

if "selected_provider_for_route" not in st.session_state:
    st.session_state.selected_provider_for_route = None

# Inicializa el estado de la pestaña de la pagina de recomendaciones
if "current_tab_recomendacion" not in st.session_state:
    st.session_state.current_tab_recomendacion = "Resumen"

# Extract user data from session state
categoria = st.session_state.get("selected_categoria", "")
categoria = text_cleaning(categoria)

nivel_triage = st.session_state.get("decision_triage")
especialidad = st.session_state.get("decision_especialidad", "")
user_dept = st.session_state.get("departamento", "")
user_city = st.session_state.get("ciudad", "")
user_location = st.session_state.get("ubicacion_usuario")

# -------------------------------------------------------------------------
# Cargar datos de recomendación una sola vez
# if not st.session_state.recommendation_data_loaded:
with st.spinner("🔄 Cargando sistema de recomendación..."):
    try:
        df_correspondencia = build_triage_correspondence_table(
            threshold=0.7, top_k=2, method="semantic"
        )

        recomendacion = get_recommended_services(
            categoria=categoria,
            nivel_triage=nivel_triage,
            especialidad=especialidad,
            df_correspondencia=df_correspondencia,
        )

        servicios_recomendados = recomendacion["servicios"]
        scores = recomendacion["scores"]
        tipo_match = recomendacion["tipo"]

        df_prestadores = load_and_prepare_provider_data()

        providers_filtered = filter_providers_by_service_and_location(
            servicios=servicios_recomendados,
            departamento=user_dept,
            municipio=user_city,
            user_location=user_location,
            max_distance_km=100.0,
        )

        # Guardar en session state
        st.session_state.recommended_providers = providers_filtered
        st.session_state.servicios_recomendados = servicios_recomendados
        st.session_state.scores_recomendacion = scores
        st.session_state.tipo_match = tipo_match
        st.session_state.df_correspondencia = df_correspondencia
        st.session_state.df_prestadores = df_prestadores
        st.session_state.recommendation_data_loaded = True

    except Exception as e:
        st.error(f"❌ Error al cargar el sistema de recomendación: {str(e)}")
        st.exception(e)
        st.stop()

# Recuperar datos del session state
providers_filtered = st.session_state.recommended_providers
servicios_recomendados = st.session_state.servicios_recomendados
scores = st.session_state.scores_recomendacion
tipo_match = st.session_state.tipo_match
df_correspondencia = st.session_state.df_correspondencia
df_prestadores = st.session_state.df_prestadores

# -------------------------------------------------------------------------
## Navigation menu con option_menu

selected_tab = options_navigation_recomendacion(
    st.session_state.current_tab_recomendacion,
)

st.markdown("")

# -------------------------------------------------------------------------
## TAB: Resumen

if selected_tab == "Resumen":
    if len(providers_filtered) > 0:
        st.info(
            f"🔎  Se identificaron **{len(providers_filtered)}** prestadores recomendados"
        )

        # Display top 3 providers
        st.markdown("### Top 3 - Prestadores Recomendados")
        st.markdown("")

        for idx, row in providers_filtered.head(5).iterrows():
            with st.container():
                col1, col2, col3 = st.columns([5, 2, 1])

                with col1:
                    st.markdown(f"**{row['prestador']}**")
                    st.caption(f"📌 {row['direccion']}")
                    st.caption(
                        f"🏥 Servicio: {row['servicio_prestador'].replace('_', ' ').title()}"
                    )
                    if "distancia_km" in row and row["distancia_km"] is not None:
                        st.caption(f"📏 Distancia: {row['distancia_km']:.2f} km")
                    st.caption(f"temp: {row.get('prioridad_recomendacion', 'N/A')}")

                with col2:
                    if st.button(
                        "🗺️ Ver Ruta", key=f"ver_ruta_{idx}", use_container_width=True
                    ):
                        st.session_state.selected_provider_for_route = idx
                        st.session_state.current_tab_recomendacion = "Ruta"
                        st.rerun()

                st.markdown("---")

        # Show full table
        with st.expander("📊 Ver total prestadores recomendados", expanded=False):
            display_cols = [
                "prestador",
                # "servicio_prestador",
                "direccion",
                "telefono_fijo",
            ]
            if "distancia_km" in providers_filtered.columns:
                display_cols.append("distancia_km")
            # display_cols.append("prioridad_recomendacion")

            st.dataframe(
                providers_filtered[display_cols].head(20),
                use_container_width=True,
            )
    else:
        st.warning(
            f"⚠️ No se encontraron prestadores en {user_city}, {user_dept} "
            f"para los servicios recomendados: {', '.join(servicios_recomendados)}"
        )
        st.info(
            "💡 Intenta ampliar el radio de búsqueda o considera prestadores en ciudades cercanas."
        )

    st.markdown("___")

    # Show matching info
    with st.expander("ℹ️ Información de Triage → Servicios", expanded=False):
        st.write(f"**Nivel de triage:** {nivel_triage}")
        st.write(f"**Especialidad requerida:** {especialidad}")
        st.write(f"**Servicios sugeridos:** {', '.join(servicios_recomendados)}")
        st.write(f"**Tipo de coincidencia:** {tipo_match}")
        if scores:
            st.write(f"**Confianza:** {', '.join([f'{s:.2f}' for s in scores])}")

    # DEBUG info
    show_recommendation_debug_info(
        categoria=categoria,
        nivel_triage=nivel_triage,
        especialidad=especialidad,
        user_dept=user_dept,
        user_city=user_city,
        user_location=user_location,
        df_correspondencia=df_correspondencia,
        servicios_recomendados=servicios_recomendados,
        scores=scores,
        tipo_match=tipo_match,
        df_prestadores=df_prestadores,
        providers_filtered=providers_filtered,
        expanded=False,
    )

# -------------------------------------------------------------------------
## TAB: Ruta

elif selected_tab == "Ruta":
    if len(providers_filtered) == 0:
        st.warning("⚠️ No hay prestadores disponibles para mostrar en el mapa.")
    else:
        st.markdown("#### Seleccione un prestador para ver la ruta")
        st.markdown("")

        # Checkbox selection for top 5 providers
        top3 = providers_filtered.head(5)

        selected_provider_idx = None

        for idx, row in top3.iterrows():
            col1, col2, col3 = st.columns([4, 1, 2])

            with col1:
                is_selected = st.checkbox(
                    f"**{row['prestador']}** - {row['direccion']}",
                    key=f"provider_checkbox_{idx}",
                    value=(st.session_state.selected_provider_for_route == idx),
                )

                if is_selected:
                    selected_provider_idx = idx
                    st.session_state.selected_provider_for_route = idx

            with col2:
                if "distancia_km" in row and row["distancia_km"] is not None:
                    st.caption(f"📏 {row['distancia_km']:.2f} km")

        st.markdown("---")

        # Display map with route
        if selected_provider_idx is not None:
            selected_row = providers_filtered.loc[selected_provider_idx]

            st.markdown(f"#### 📍 Ruta hacia: **{selected_row['prestador']}**")
            st.markdown("")

            # Create map centered between user and provider
            user_lat = user_location["lat"]
            user_lng = user_location["lng"]
            provider_lat = selected_row["lat"]
            provider_lng = selected_row["lng"]

            # Calculate center point
            center_lat = (user_lat + provider_lat) / 2
            center_lng = (user_lng + provider_lng) / 2

            # -------
            ## External navigation link

            # st.markdown("#### Navegación externa")

            google_maps_url = (
                f"https://www.google.com/maps/dir/?api=1"
                f"&origin={user_lat},{user_lng}"
                f"&destination={provider_lat},{provider_lng}"
                f"&travelmode=driving"
            )

            st.markdown(
                f"[🗺️ Abrir en Google Maps]({google_maps_url})",
                unsafe_allow_html=True,
            )

            st.markdown("---")

            # ------
            # Create map
            m = folium.Map(
                location=[center_lat, center_lng],
                zoom_start=13,
                tiles="OpenStreetMap",
            )

            # Add user marker (blue)
            folium.Marker(
                location=[user_lat, user_lng],
                popup="Tu ubicación",
                tooltip=st.session_state.get("cached_address", "N/A"),
                icon=folium.Icon(color="green", icon="user", prefix="fa"),
            ).add_to(m)

            # Add provider marker (red)
            folium.Marker(
                location=[provider_lat, provider_lng],
                popup=f"<b>{selected_row['prestador']}</b><br>{selected_row['direccion']}",
                tooltip=selected_row["prestador"],
                icon=folium.Icon(color="red", icon="hospital", prefix="fa"),
            ).add_to(m)

            # Add line between user and provider
            folium.PolyLine(
                locations=[[user_lat, user_lng], [provider_lat, provider_lng]],
                color="blue",
                weight=3,
                opacity=0.7,
                popup="Ruta estimada",
            ).add_to(m)

            # Add distance marker at midpoint
            if (
                "distancia_km" in selected_row
                and selected_row["distancia_km"] is not None
            ):
                folium.Marker(
                    location=[center_lat, center_lng],
                    icon=folium.DivIcon(
                        html=f"""
                        <div style="
                            background-color: white;
                            border: 2px solid #1976D2;
                            border-radius: 6px;
                            padding: 6px 75px 6px 4px;
                            font-weight: bold;
                            color: #1976D2;
                            text-align: center;
                            font-size: 12px;
                            transform: translate(-50%, -50%);
                            position: relative;
                            white-space: nowrap;
                            box-shadow: 0 0 4px rgba(0,0,0,0.2);
                        ">
                            📏 {selected_row["distancia_km"]:.2f} km
                        </div>
                        """,
                        icon_anchor=(
                            0,
                            0,
                        ),  # anchor top-left, but CSS translate recenters it
                    ),
                ).add_to(m)

            # Fit bounds to show both markers
            m.fit_bounds([[user_lat, user_lng], [provider_lat, provider_lng]])

            # Display map
            center_column = st.columns([1, 8, 1])[1]
            with center_column:
                st_folium(m, width=None, height=500, returned_objects=[])

            st.markdown("")

            # Provider details
            st.markdown("#### Detalles del prestador")
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Nombre:** {selected_row['prestador']}")
                st.write(f"**Dirección:** {selected_row['direccion']}")
                st.write(
                    f"**Servicio:** {selected_row['servicio_prestador'].replace('_', ' ').title()}"
                )

            with col2:
                st.write(f"**Teléfono:** {selected_row.get('telefono_fijo', 'N/A')}")
                if (
                    "distancia_km" in selected_row
                    and selected_row["distancia_km"] is not None
                ):
                    st.write(f"**Distancia:** {selected_row['distancia_km']:.2f} km")

        else:
            st.info("👆 Seleccione un prestador para visualizar la ruta en el mapa.")

# -------------------------------------------------------------------------
## Botón para regresar al inicio

st.markdown("___")

col_back = st.columns([2, 4, 2])[0]
with col_back:
    if st.button("← Volver al Inicio", use_container_width=True):
        # Reset recommendation state
        st.session_state.recommendation_step = False
        st.session_state.recommendation_data_loaded = False
        st.session_state.selected_provider_for_route = None
        st.session_state.current_tab_triage = "Mapa ubicación"
        st.switch_page("app.py")
