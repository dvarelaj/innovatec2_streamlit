import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster, LocateControl, Fullscreen

from utils.ui_geocode import get_coordinates_co


def map_triage_locate(
    ubicacion_usuario, modo_ubicacion="Manual", width: int = 800, height: int = 500
):
    """
    Display an interactive Folium map where the user can locate themselves.

    This function renders a Folium map embedded inside Streamlit using `st_folium`.
    It includes several tile layers, location markers for major Colombian cities,
    and map controls such as zoom, fullscreen, and locate buttons.

    Parameters
    ----------
    width : int, optional
        The width (in pixels) of the map container. Default is 800.
    height : int, optional
        The height (in pixels) of the map container. Default is 500.

    Returns
    -------
    dict
        The output object returned by `st_folium`, containing information such as
        the last clicked coordinates, map bounds, and zoom level.
        Example:
            output = map_triage_locate()
            coords = output["last_clicked"]
    """
    # --- Determine initial map center ---

    # Ensure city coordinates exist in session state
    if "city_lat" not in st.session_state or "city_lon" not in st.session_state:
        st.session_state.city_lat, st.session_state.city_lon = (
            4.5709,
            -74.2973,
        )  # Default center (Colombia)

    # If we already queried the city coordinates once, reuse them
    if not st.session_state.get("coordinates_queried_ciudad", False):
        # Only run the geocoding once
        name_location = f"{st.session_state.get('ciudad', 'Colombia')}, {st.session_state.get('departamento', '')}"
        coords = get_coordinates_co(name_location)

        if coords:  # If geocoding succeeded
            st.session_state.city_lat, st.session_state.city_lon = coords
        else:
            st.warning(
                f"No se encontraron coordenadas para '{st.session_state.get('ciudad', 'Desconocida')}'."
            )
            st.session_state.city_lat, st.session_state.city_lon = (4.5709, -74.2973)

        st.session_state.coordinates_queried_ciudad = True

    # Initialize map centered on user's city
    # If modo_ubicacion is "Auto", disable dragging to avoid conflicts with LocateControl
    if modo_ubicacion == "Auto":
        m = folium.Map(
            location=[st.session_state["city_lat"], st.session_state["city_lon"]],
            zoom_start=15,
            dragging=False,  # ❌ Disable dragging
            scroll_wheel_zoom=False,  # ❌ Disable scroll wheel zoom
            touch_zoom=False,  # ❌ Disable touch zoom
            double_click_zoom=False,  # ❌ Disable double click zoom
        )
    else:
        # --- Center map on user's selected location if available ---
        if ubicacion_usuario:
            # Center on user's selected location
            m = folium.Map(
                location=[ubicacion_usuario["lat"], ubicacion_usuario["lng"]],
                zoom_start=15,
            )
        else:
            # Center on city coordinates
            m = folium.Map(
                location=[st.session_state["city_lat"], st.session_state["city_lon"]],
                zoom_start=13,
            )
    # --- Example markers for key Colombian cities ---
    coords = {
        "Bogotá": [4.65, -74.1],
        "Medellín": [6.25, -75.57],
        "Cali": [3.43, -76.52],
    }
    cluster_ciudades = MarkerCluster(name="Ciudades").add_to(m)

    for city, coord in coords.items():
        folium.Marker(
            location=coord,
            popup=city,
            tooltip=city,
            icon=folium.Icon(color="red", icon="hospital", prefix="fa"),
        ).add_to(cluster_ciudades)

    # --- If the user has already selected a location, show the marker ---
    if modo_ubicacion == "Manual" and ubicacion_usuario:
        user_lat = ubicacion_usuario["lat"]
        user_lng = ubicacion_usuario["lng"]
        folium.Marker(
            location=[user_lat, user_lng],
            tooltip="Tu ubicación",
            icon=folium.Icon(color="green", icon="user", prefix="fa"),
        ).add_to(m)

    # --- Base map layers ---
    folium.TileLayer(
        "OpenStreetMap",
        name="Mapa base #1",
        show=False,
    ).add_to(m)

    # folium.TileLayer(
    #     "CartoDB positron",
    #     name="Mapa #2",
    #     attr="© OpenStreetMap contributors",
    #     show=False,
    # ).add_to(m2)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri — Source: Esri, DeLorme, NAVTEQ, USGS, and others",
        name="Mapa base #2",
        show=True,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri, Maxar, Earthstar Geographics, and the GIS User Community",
        name="Imágenes satelitales",
        show=False,
    ).add_to(m)

    # --- Map controls ---
    # Enable user location
    if modo_ubicacion == "Auto":
        LocateControl(
            auto_start=True,
            keepCurrentZoomLevel=False,
            flyTo=True,
            locateOptions={"maxZoom": 16},
        ).add_to(m)
    else:
        LocateControl(
            auto_start=False,
            keepCurrentZoomLevel=False,
            locateOptions={"maxZoom": 16},
        ).add_to(m)

    # Fullscreen button
    Fullscreen(
        position="topright",
        title="Expandir",
        title_cancel="Salir",
        force_separate_button=True,
    ).add_to(m)

    # Layer control to switch between base maps
    folium.LayerControl().add_to(m)

    # --- Map plugins ---
    # Measure control (disabled)
    # m.add_child(folium.plugins.MeasureControl())

    # Mini map (disabled)
    # MiniMap().add_to(m)

    # --- Render in Streamlit ---
    output = st_folium(m, width=width, height=height)

    return output
