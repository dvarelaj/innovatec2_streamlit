import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderRateLimited, GeocoderUnavailable
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


@st.cache_data(show_spinner=False)
def geocode_address(address):
    """Get coordinates (lat, lon) from an address using OpenStreetMap (Nominatim)."""
    geolocator = Nominatim(user_agent="triage_app_geocode")
    try:
        location = geolocator.geocode(address + ", Colombia", timeout=10)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
