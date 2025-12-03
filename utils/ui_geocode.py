import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderRateLimited, GeocoderUnavailable
import time
import requests


###. OpenStreetMap Nominatim Geocoding #####
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

    geolocator = Nominatim(user_agent="triage_app_geocode")

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


@st.cache_data(show_spinner=False)
def reverse_geocode(lat, lon):
    """Get human-readable address from geographic coordinates using OpenStreetMap (Nominatim).

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        str: Full address in readable format if found,
             "Address not found" if no results,
             or "Error connecting to service" if there are connection issues.

    Raises:
        Does not raise exceptions directly, handles them internally.

    Examples:
        >>> reverse_geocode(40.7128, -74.0060)
        'New York, United States'
    """
    geolocator = Nominatim(user_agent="triage_app_geocode_reverse")
    try:
        location = geolocator.reverse((lat, lon), language="es")
        if location and location.address:
            return location.address
        else:
            return "Dirección no encontrada"
    except (GeocoderTimedOut, GeocoderUnavailable):
        return "Error al conectar con el servicio"


#####. ArcGIS Public Geocoding (Alternative) #####


@st.cache_data(show_spinner=False)
def geocode_address_arcgis(address: str):
    """
    Geocoding: Dirección -> Coordenadas
    """
    url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"

    # Es buena práctica limpiar la dirección
    clean_address = address.strip()
    if not clean_address:
        return None

    params = {
        "f": "json",
        "singleLine": f"{clean_address}, Colombia",  # Forzamos búsqueda en Colombia
        "maxLocations": 1,
        "outFields": "Match_addr,Addr_type",
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()  # Lanza error si hay problemas de conexión
        data = response.json()

        if data.get("candidates"):
            top = data["candidates"][0]
            lat = top["location"]["y"]
            lng = top["location"]["x"]
            formatted = top["address"]
            return {"lat": lat, "lng": lng, "address": formatted}

    except Exception as e:
        st.error(f"Error conectando con el servicio de mapas: {e}")
        return None

    return None


@st.cache_data(show_spinner=False)
def reverse_geocode_arcgis(lat: float, lng: float):
    """
    Reverse Geocoding: Coordenadas -> Dirección aproximada
    """
    url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode"

    params = {
        "f": "json",
        "location": f"{lng},{lat}",  # Nota: ArcGIS usa x,y (lng,lat)
        "distance": 100,  # Buscar en un radio de 100 metros
        "outSR": "",
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "address" in data:
                return data["address"]["Match_addr"]
    except Exception:
        return "Dirección no encontrada"

    return "Dirección no encontrada"
