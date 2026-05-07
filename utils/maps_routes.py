"""
Módulo de Enrutamiento con Google Maps Routes API.

Reemplaza la línea recta de Folium (ORMS) de la v1 por rutas reales
usando la Routes API v2 de Google Maps.

La Routes API devuelve:
- Polilínea codificada (encoded polyline) con la ruta real por carretera
- Distancia real en metros
- Tiempo estimado de viaje en segundos

Referencia: https://developers.google.com/maps/documentation/routes
"""

import requests
import polyline  # Decodifica encoded polylines de Google
import streamlit as st
from typing import Optional


# -------------------------------------------------------------------------
# Constante — endpoint de la Routes API v2
# -------------------------------------------------------------------------

ROUTES_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"


# -------------------------------------------------------------------------
# Función principal — obtener ruta real entre dos puntos
# -------------------------------------------------------------------------

@st.cache_data(show_spinner=False, ttl=600)
def get_route_google_maps(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    api_key: str,
    travel_mode: str = "DRIVE",
) -> dict:
    """
    Obtiene la ruta real por carretera entre dos puntos usando Google Routes API.

    La Routes API v2 es la evolución de Directions API — más precisa,
    más rápida y con soporte para tráfico en tiempo real.

    Parameters
    ----------
    origin_lat, origin_lng : float
        Coordenadas del punto de origen (ubicación del usuario).
    dest_lat, dest_lng : float
        Coordenadas del destino (prestador de salud).
    api_key : str
        API Key de Google Maps con Routes API habilitada.
    travel_mode : str
        Modo de viaje: "DRIVE", "WALK", "BICYCLE", "TRANSIT".

    Returns
    -------
    dict
        {
            "coords": [(lat, lng), ...],   # Lista de coordenadas de la ruta
            "distancia_m": int,            # Distancia en metros
            "distancia_km": float,         # Distancia en kilómetros
            "duracion_seg": int,           # Duración en segundos
            "duracion_texto": str,         # Duración legible (ej: "25 min")
            "exito": bool,
            "error": str | None
        }
    """

    fallback = {
        "coords": [(origin_lat, origin_lng), (dest_lat, dest_lng)],
        "distancia_m": 0,
        "distancia_km": 0.0,
        "duracion_seg": 0,
        "duracion_texto": "N/A",
        "exito": False,
        "error": None,
    }

    # Construir el body del request en formato JSON
    # La Routes API usa REST con POST y un body estructurado
    body = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin_lat,
                    "longitude": origin_lng,
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": dest_lat,
                    "longitude": dest_lng,
                }
            }
        },
        "travelMode": travel_mode,
        "routingPreference": "TRAFFIC_AWARE",  # Considera tráfico en tiempo real
        "computeAlternativeRoutes": False,
        "routeModifiers": {
            "avoidTolls": False,
            "avoidHighways": False,
        },
        "languageCode": "es-CO",  # Instrucciones en español colombiano
        "units": "METRIC",
    }

    # Headers requeridos por la Routes API v2
    # X-Goog-FieldMask especifica qué campos quieres en la respuesta
    # Esto reduce el costo de la llamada (solo pagas por lo que pides)
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "routes.duration,"
            "routes.distanceMeters,"
            "routes.polyline.encodedPolyline"
        ),
    }

    try:
        response = requests.post(
            ROUTES_API_URL,
            json=body,
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            fallback["error"] = (
                f"Error Routes API: {response.status_code} — {response.text[:200]}"
            )
            return fallback

        data = response.json()

        # Verificar que hay rutas en la respuesta
        if not data.get("routes"):
            fallback["error"] = "No se encontraron rutas entre los dos puntos."
            return fallback

        ruta = data["routes"][0]

        # Extraer distancia
        distancia_m = ruta.get("distanceMeters", 0)
        distancia_km = round(distancia_m / 1000, 2)

        # Extraer duración — viene como "1234s" (segundos con letra s)
        duracion_str = ruta.get("duration", "0s")
        duracion_seg = int(duracion_str.replace("s", ""))
        duracion_texto = _segundos_a_texto(duracion_seg)

        # Decodificar la polilínea codificada de Google
        # Google usa su propio algoritmo de codificación para comprimir coordenadas
        encoded = ruta.get("polyline", {}).get("encodedPolyline", "")
        if encoded:
            coords = polyline.decode(encoded)  # Lista de (lat, lng)
        else:
            coords = [(origin_lat, origin_lng), (dest_lat, dest_lng)]

        return {
            "coords": coords,
            "distancia_m": distancia_m,
            "distancia_km": distancia_km,
            "duracion_seg": duracion_seg,
            "duracion_texto": duracion_texto,
            "exito": True,
            "error": None,
        }

    except requests.exceptions.Timeout:
        fallback["error"] = "Tiempo de espera agotado con Google Maps."
        return fallback
    except Exception as e:
        fallback["error"] = f"Error inesperado: {str(e)}"
        return fallback


# -------------------------------------------------------------------------
# Función auxiliar — convierte segundos a texto legible
# -------------------------------------------------------------------------

def _segundos_a_texto(segundos: int) -> str:
    """Convierte segundos a formato legible. Ej: 3720 → '1 h 2 min'"""
    if segundos <= 0:
        return "N/A"
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    if horas > 0:
        return f"{horas} h {minutos} min"
    return f"{minutos} min"
