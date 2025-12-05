"""
Provider recommendation engine for RutaSalud.

This module handles the complete workflow of recommending healthcare providers
based on user triage results and location.
"""

import pandas as pd
import streamlit as st
from typing import Optional, Dict, List
from utils.input_data.triage_symptoms import build_triage_combinations
from utils.matching_utils.triage_matching import (
    build_correspondence_table,
)
from utils.input_data.providers_utils import (
    clean_providers_data,
    merge_provider_locations,
)

from utils.general_utils import text_cleaning


@st.cache_data(show_spinner=False, ttl=3600)
def load_and_prepare_provider_data(
    path_prestadores: str = "data/prestadores_mapa.xlsx",
    path_prestadores_urg: str = "data/prestadores_urg.xlsx",
) -> pd.DataFrame:
    """
    Load, clean, and merge provider datasets.

    This function is cached to avoid reloading data on every rerun.
    Cache expires after 1 hour (ttl=3600).

    Parameters
    ----------
    path_prestadores : str
        Path to main providers Excel file.
    path_prestadores_urg : str
        Path to urgent care providers Excel file.

    Returns
    -------
    pd.DataFrame
        Cleaned and merged provider dataset with standardized columns.
    """
    # Load raw data
    df_prestadores = pd.read_excel(path_prestadores)
    df_prestadores_urg = pd.read_excel(path_prestadores_urg)

    # Clean both datasets
    prestadores_clean = clean_providers_data(df_prestadores, verbose=False)
    prestadores_urg_clean = clean_providers_data(df_prestadores_urg, verbose=False)

    # Merge location data from urgent care
    prestadores_final = merge_provider_locations(
        prestadores_clean, prestadores_urg_clean, verbose=False
    )

    return prestadores_final


@st.cache_data(show_spinner=True, ttl=3600)
def build_triage_correspondence_table(
    path_triage: str = "data/triage_sintomas.xlsx",
    path_prestadores: str = "data/prestadores_mapa.xlsx",
    path_prestadores_urg: str = "data/prestadores_urg.xlsx",
    threshold: float = 0.7,
    top_k: int = 3,
    method: str = "semantic",
) -> pd.DataFrame:
    """
    Build the complete triage-to-service correspondence table.

    This function is cached to avoid rebuilding the table on every rerun.
    Cache expires after 1 hour.

    Parameters
    ----------
    path_triage : str
        Path to triage symptoms Excel file.
    path_prestadores : str
        Path to main providers Excel file.
    path_prestadores_urg : str
        Path to urgent care providers Excel file.
    threshold : float, optional
        Minimum similarity score for matching (0-1).
    top_k : int, optional
        Number of service suggestions per triage case.
    method : str, optional
        Matching method: 'semantic' or 'fuzzy'.

    Returns
    -------
    pd.DataFrame
        Correspondence table with columns:
        ['categoria','nivel_triage', 'modalidad_requerida', 'especialidad_requerida',
         'servicios_sugeridos', 'scores', 'tipo_coincidencia']
    """
    # Build triage combinations
    df_triage = build_triage_combinations(path_triage)

    # Load and prepare provider data
    prestadores_final = load_and_prepare_provider_data(
        path_prestadores, path_prestadores_urg
    )

    # Build correspondence table
    df_corr = build_correspondence_table(
        df_sintomas=df_triage,
        df_prestadores=prestadores_final,
        threshold=threshold,
        top_k=top_k,
        method=method,
        verbose=False,
    )

    return df_corr


def get_recommended_services(
    categoria: str,
    nivel_triage: str,
    especialidad: str,
    df_correspondencia: pd.DataFrame,
) -> Dict[str, List]:
    """
    Get recommended services for a specific triage result.

    Parameters
    ----------
    categoria : str
        Triage category.
    nivel_triage : str
        Triage level (T1, T2, T3, T4, T5).
    especialidad : str
        Required specialty (normalized).
    df_correspondencia : pd.DataFrame
        Pre-built correspondence table.

    Returns
    -------
    dict
        Dictionary with keys:
        - 'servicios': list of recommended service names
        - 'scores': list of confidence scores
        - 'tipo': matching type used
    """
    # Normalize specialty for matching
    especialidad_norm = especialidad.lower().strip()

    # Find matching row in correspondence table
    mask = (
        (df_correspondencia["categoria"] == categoria)
        & (df_correspondencia["nivel_triage"] == nivel_triage)
        & (df_correspondencia["especialidad_requerida"] == especialidad_norm)
    )

    matches = df_correspondencia[mask]

    if not matches.empty:
        row = matches.iloc[0]
        return {
            "servicios": row["servicios_sugeridos"],
            "scores": row["scores"],
            "tipo": row["tipo_coincidencia"],
        }
    else:
        # Fallback to generic services
        if nivel_triage in ["T1", "T2", "T3"]:
            return {
                "servicios": ["urgencias_medico_general"],
                "scores": [1.0],
                "tipo": "fallback",
            }
        else:
            return {
                "servicios": ["consulta_medicina_general"],
                "scores": [1.0],
                "tipo": "fallback",
            }


def filter_providers_by_service_and_location(
    servicios: List[str],
    departamento: str,
    municipio: str,
    path_prestadores: str = "data/prestadores_mapa.xlsx",
    path_prestadores_urg: str = "data/prestadores_urg.xlsx",
    user_location: Optional[Dict] = None,
    max_distance_km: float = 100.0,
) -> pd.DataFrame:
    """
    Filter providers by recommended services and location.

    Parameters
    ----------
    df_prestadores : pd.DataFrame
        Full provider dataset.
    servicios : list of str
        List of recommended service names.
    departamento : str
        User's department.
    municipio : str
        User's municipality.
    user_location : dict, optional
        User's coordinates: {"lat": float, "lng": float}.
        If provided, calculates distances.
    max_distance_km : float, optional
        Maximum distance for filtering (if user_location provided).

    Returns
    -------
    pd.DataFrame
        Filtered and sorted provider dataset.
    """
    # Normalize and title the user location inputs
    departamento = text_cleaning(departamento).title()
    municipio = text_cleaning(municipio).title()

    # Load and prepare provider data
    prestadores_final = load_and_prepare_provider_data(
        path_prestadores, path_prestadores_urg
    )

    # st.error(f"Total providers available: {len(prestadores_final)}")
    # st.warning(
    #     prestadores_final[prestadores_final["departamento"] == "Antioquia"][
    #         "municipio"
    #     ].unique()
    # )

    # Filter by service
    filtered = prestadores_final[
        prestadores_final["servicio_prestador"].isin(servicios)
    ].copy()

    # st.error(f"Providers after service filter: {len(filtered)}")

    # Filter by location (department and municipality)
    filtered = filtered[
        (filtered["departamento"].str.lower() == departamento.lower())
        & (filtered["municipio"].str.lower() == municipio.lower())
    ]

    # st.warning(f"Filtering providers in {municipio}, {departamento}")
    # st.error(f"Providers after location filter: {len(filtered)}")

    # Calculate distances if user location provided
    if user_location and len(filtered) > 0:
        from math import radians, cos, sin, asin, sqrt

        def haversine(lat1, lon1, lat2, lon2):
            """Calculate distance between two points on Earth (km)."""
            R = 6371  # Earth radius in kilometers
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            return R * c

        user_lat = user_location["lat"]
        user_lng = user_location["lng"]

        filtered["distancia_km"] = filtered.apply(
            lambda row: haversine(user_lat, user_lng, row["lat"], row["lng"]), axis=1
        )

        # Filter by distance
        filtered = filtered[filtered["distancia_km"] <= max_distance_km]

        # Sort by distance first, then by priority
        filtered = filtered.sort_values(
            by=["distancia_km", "prioridad_recomendacion"], ascending=[True, True]
        )
    else:
        # Sort by priority only
        filtered = filtered.sort_values(by="prioridad_recomendacion", ascending=True)

    return filtered
