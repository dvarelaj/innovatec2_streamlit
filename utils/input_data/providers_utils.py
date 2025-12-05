"""
Data cleaning utilities for healthcare provider datasets.
"""

import pandas as pd
from typing import List, Optional
from utils.general_utils import text_cleaning
import streamlit as st

PROVIDERS_GENERAL_PATH = (
    "https://docs.google.com/uc?export=download&id=1U87jmsTC5KUq-_zugFNFrRvu7HD0RE8Q"
)
PROVIDERS_URG_PATH = (
    "https://docs.google.com/uc?export=download&id=1XNZRTafStxxSAqcN1u1LIBBCbKY_dZM2"
)


@st.cache_data(show_spinner=False)
def clean_providers_data(
    df: pd.DataFrame,
    servicios_prestadores: Optional[List[str]] = None,
    prestadores_to_drop: Optional[List[str]] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Clean and standardize healthcare provider (prestadores) data.

    This function performs a comprehensive cleaning pipeline on provider datasets:
    1. Normalizes column names (lowercase, replace spaces/dots with underscores)
    2. Removes blacklisted providers and null values
    3. Filters out direccionamiento == 9 (excluded service routing)
    4. Removes providers with missing or zero coordinates
    5. Applies text cleaning to service names (concepto_factura)
    6. Filters by allowed service types
    7. Standardizes column names and formats department/municipality names
    8. Selects and renames final columns for consistency

    Parameters
    ----------
    df : pd.DataFrame
        Raw provider data loaded from Excel (e.g., prestadores_mapa.xlsx).
    servicios_prestadores : list of str, optional
        List of allowed service names (after text_cleaning). If None, uses default list.
    prestadores_to_drop : list of str, optional
        List of provider names to exclude. If None, uses default blacklist.
    verbose : bool, optional
        If True, print progress messages during cleaning. If False, only show final message (default: True).

    Returns
    -------
    pd.DataFrame
        Cleaned provider data with standardized columns:
        - prestador, sucursal, departamento, municipio, direccion
        - lat, lng, servicio_prestador, prioridad_recomendacion
        - horario, telefono_fijo, telefono_celular

    Examples
    --------
    >>> df_raw = pd.read_excel("../data/prestadores_mapa.xlsx")
    >>> df_clean = clean_prestadores_data(df_raw)
    >>> print(df_clean.columns.tolist())
    ['prestador', 'sucursal', 'departamento', 'municipio', 'direccion', 'lat', 'lng', ...]
    """

    # Default blacklist of providers to exclude
    if prestadores_to_drop is None:
        prestadores_to_drop = [
            "ORDEN DE COMPRA PUNTUAL",
            "IPS DE ATENCION INICIALPOR CONFIRMAR",
        ]

    # Default allowed services (normalized with text_cleaning)
    if servicios_prestadores is None:
        servicios_prestadores = [
            "urgencias_medico_general",
            "consulta_no_programada",
            "urgencias_riesgo_biologico",
            "consulta_ortopedista",
            "urgencias_ortopedista",
            "consulta_medicina_fisica_y_de_deporte_l",
            "consulta_odontologica",
            "consulta_prioritaria_odontologia_l",
            "urgencias_odontologia_l",
            "consulta_prioritaria_de_oftalmologia_l",
            "consulta_oftalmologia",
            "cirugia_oftalmologia",
            "urgencias_oftalmologia",
            "consulta_medicina_interna",
            "consulta_medicin_interna_telemedicina_l",
            "consulta_urologia",
            "cirugia_urologia",
            "consulta_otorrinolaringologia",
            "cirugia_otorrinolaringologia",
            "consulta_dermatologia_telemedicina_l",
            "consulta_y_procedimientos_dermatologia",
            "urgencia_cirugia_plastica",
            "consulta_psicologo_y_terapia_psicologica",
            "consulta_neurologo",
            "consulta_cirujano_general",
        ]

    # Create a copy to avoid modifying the original
    df_clean = df.copy()

    # --- Step 1: Normalize column names ---
    df_clean.columns = [
        c.lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("/", "_")
        .replace("__", "_")
        for c in df_clean.columns
    ]

    if verbose:
        print(f"✓ {df_clean.shape[0]} registros iniciales cargados")

    # --- Step 2: Remove blacklisted providers and null values ---
    df_clean = df_clean[
        df_clean["prestador"].notnull()
        & ~df_clean["prestador"].isin(prestadores_to_drop)
    ]
    if verbose:
        print(
            f"✓ {df_clean.shape[0]} registros después de eliminar prestadores no válidos"
        )

    # --- Step 3: Filter out direccionamiento == 9 ---
    df_clean = df_clean[df_clean["direccionamiento"] != 9]
    if verbose:
        print(
            f"✓ {df_clean.shape[0]} registros después de filtrar direccionamiento != 9"
        )

    # --- Step 4: Remove providers with missing/zero coordinates ---
    df_clean = df_clean[
        df_clean["valor_latitud"].notnull()
        & df_clean["valor_longitud"].notnull()
        & (df_clean["valor_latitud"] != 0)
        & (df_clean["valor_longitud"] != 0)
    ]
    if verbose:
        print(
            f"✓ {df_clean.shape[0]} registros después de eliminar coordenadas inválidas"
        )

    # --- Step 5: Apply text cleaning to service names ---
    df_clean["servicio_prestador"] = df_clean["concepto_factura"].apply(text_cleaning)

    # --- Step 6: Filter by allowed service types ---
    df_clean = df_clean[df_clean["servicio_prestador"].isin(servicios_prestadores)]

    # --- step 6.5: Rename specific service names for downstream processing ---
    df_clean["servicio_prestador"] = df_clean["servicio_prestador"].replace(
        {
            "consulta_medicina_fisica_y_de_deporte_l": "consulta_deportologia",
            "consulta_prioritaria_odontologia_l": "consulta_prioritaria_odontologia",
            "urgencias_odontologia_l": "urgencias_odontologia",
            "consulta_prioritaria_de_oftalmologia_l": "consulta_prioritaria_oftalmologia",
            "consulta_medicin_interna_telemedicina_l": "consulta_medicina_interna_telemedicina",
            "consulta_dermatologia_telemedicina_l": "consulta_dermatologia_telemedicina",
            "consulta_no_programada": "consulta_medicina_general",
            "consulta_cirujano_general": "consulta_cirugia_general",
        }
    )

    # Final message always shown
    print(f"✓ Limpieza completada: {df_clean.shape[0]} registros de prestadores\n")

    # --- Step 7: Format department and municipality names ---
    df_clean["departamento"] = df_clean["departamento"].str.title()
    df_clean["municipio"] = df_clean["municipio"].str.title()

    # --- Step 8: Select and rename columns ---
    df_clean = df_clean[
        [
            "prestador",
            "sucursal_prestador",
            "departamento",
            "municipio",
            "direccion_domicilio",
            "valor_latitud",
            "valor_longitud",
            "servicio_prestador",
            "direccionamiento",
            "horario_habil",
            "telefono",
            "telefono_celular",
        ]
    ]

    df_clean = df_clean.rename(
        columns={
            "sucursal_prestador": "sucursal",
            "direccion_domicilio": "direccion",
            "valor_latitud": "lat",
            "valor_longitud": "lng",
            "direccionamiento": "prioridad_recomendacion",
            "horario_habil": "horario",
            "telefono": "telefono_fijo",
        }
    )

    return df_clean


def merge_provider_locations(
    df_main: pd.DataFrame,
    df_urg: pd.DataFrame,
    key_columns: List[str] = None,
    location_columns: List[str] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Merge location data from urgent care providers into main provider dataset.

    This function updates location information (direccion, lat, lng) in the main
    provider dataset with more accurate data from the urgent care dataset. It handles
    cases where a combination of keys appears multiple times by using the first occurrence.

    The merge strategy:
    1. Extract unique key-location mappings from df_urg based on composite key
    2. For each unique key combination, use the first occurrence's location data
    3. Update matching providers in df_main with the new location data

    Parameters
    ----------
    df_main : pd.DataFrame
        Main provider dataset (e.g., prestadores_clean) to be updated.
    df_urg : pd.DataFrame
        Urgent care provider dataset (e.g., prestadores_urg_clean) with updated locations.
    key_columns : list of str, optional
        List of column names to match providers (default: ["sucursal", "departamento", "municipio"]).
        These columns form a composite key to uniquely identify providers.
    location_columns : list of str, optional
        Columns to update. Default: ["direccion", "lat", "lng"].
    verbose : bool, optional
        If True, print progress messages during merge. If False, only show final message (default: True).

    Returns
    -------
    pd.DataFrame
        Updated main provider dataset with merged location data.

    Examples
    --------
    >>> # Using default composite key (sucursal + departamento + municipio)
    >>> prestadores_merged = merge_provider_locations(
    ...     prestadores_clean,
    ...     prestadores_urg_clean
    ... )
    >>> print(f"Updated {prestadores_merged.shape[0]} providers")

    >>> # Using custom key columns
    >>> prestadores_merged = merge_provider_locations(
    ...     prestadores_clean,
    ...     prestadores_urg_clean,
    ...     key_columns=["sucursal", "departamento"]
    ... )

    Notes
    -----
    - The function creates a copy of df_main to avoid modifying the original
    - If a key combination appears multiple times in df_urg, only the first occurrence is used
    - Only providers matching all key columns will be updated
    - Prints summary statistics about the merge operation
    """

    if key_columns is None:
        key_columns = ["sucursal", "departamento", "municipio"]

    if location_columns is None:
        location_columns = ["direccion", "lat", "lng"]

    # Create a copy to avoid modifying original
    df_merged = df_main.copy()

    # Extract unique key-location mappings from urgent care data
    # drop_duplicates with keep='first' ensures we use the first occurrence
    urg_locations = df_urg[key_columns + location_columns].drop_duplicates(
        subset=key_columns, keep="first"
    )

    if verbose:
        print(
            f"📍 Encontradas {len(urg_locations)} combinaciones únicas ({', '.join(key_columns)}) en datos de urgencias"
        )

    # Track updates
    updates_count = 0
    providers_updated = []

    # Update main dataset with location data from urgent care
    for _, urg_row in urg_locations.iterrows():
        # Build composite key mask by checking all key columns match
        mask = pd.Series([True] * len(df_merged), index=df_merged.index)
        for key_col in key_columns:
            mask &= df_merged[key_col] == urg_row[key_col]

        if mask.any():
            # Update location columns for all matching rows
            for col in location_columns:
                df_merged.loc[mask, col] = urg_row[col]

            updates_count += mask.sum()
            # Store key combination for logging
            key_values = tuple(urg_row[key_col] for key_col in key_columns)
            providers_updated.append(key_values)

    # Final message always shown
    print(
        f"✓ Merge completado: {updates_count} registros actualizados de {len(providers_updated)} combinaciones únicas\n"
    )

    return df_merged
