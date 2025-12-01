import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster, LocateControl, Fullscreen
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderRateLimited
import time


@st.cache_data(show_spinner=False)
def get_coordinates_co(city_name: str):
    """Get geographic coordinates for a Colombian city.

    This function uses OpenStreetMap's Nominatim service to geocode a city name
    and retrieve its latitude and longitude coordinates.

    Args:
        city_name (str): The name of the city to geocode.

    Returns:
        A tuple containing (latitude, longitude) if the city is found, None otherwise.

    Example:
        >>> coords = get_coordinates_co("Bogotá")
        >>> print(coords)
        (4.624335, -74.063644)
    """

    geolocator = Nominatim(user_agent="triage_app_")

    for _ in range(3):  # Try up to 3 times
        try:
            time.sleep(1)
            location = geolocator.geocode(f"ciudad: {city_name}, Colombia", timeout=5)
            if location:
                return (location.latitude, location.longitude)
            else:
                location = geolocator.geocode(f"{city_name}, Colombia", timeout=5)
                if location:
                    return (location.latitude, location.longitude)
                else:
                    return None
        except (GeocoderTimedOut, GeocoderRateLimited):
            time.sleep(2)

    st.warning(f"No se pudieron obtener coordenadas para '{city_name}'.")
    return (4.5709, -74.2973)  # Fallback (Colombia center)


def map_triage_locate(ubicacion_usuario, width: int = 800, height: int = 500):
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
        coords = get_coordinates_co(st.session_state.get("ciudad", "Colombia"))

        if coords:  # If geocoding succeeded
            st.session_state.city_lat, st.session_state.city_lon = coords
        else:
            st.warning(
                f"No se encontraron coordenadas para '{st.session_state.get('ciudad', 'Desconocida')}'."
            )
            st.session_state.city_lat, st.session_state.city_lon = (4.5709, -74.2973)

        st.session_state.coordinates_queried_ciudad = True

    # Initialize map centered on user's city
    m = folium.Map(
        location=[st.session_state["city_lat"], st.session_state["city_lon"]],
        zoom_start=14,
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
    if ubicacion_usuario:
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
        name="Mapa base",
        show=True,
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
        name="Mapa topográfico",
        show=False,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri, Maxar, Earthstar Geographics, and the GIS User Community",
        name="Imágenes satelitales",
        show=False,
    ).add_to(m)

    # --- Map controls ---
    # Enable user location
    LocateControl(auto_start=False).add_to(m)

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
