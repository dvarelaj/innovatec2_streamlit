import pandas as pd
import os
from typing import Dict, List, Optional
import streamlit as st

from utils.general_utils import text_cleaning
import numpy as np

# Default path to the triage symptoms Excel file
LOCAL_SYMPTOMS_PATH = "data/triage_sintomas.xlsx"
REMOTE_SYMPTOMS_PATH = (
    "https://docs.google.com/uc?export=download&id=1igDMY2IXf8Vfogttwo3ueiHOUkYg4cM6"
)

# Determine which path to use
if os.path.exists(LOCAL_SYMPTOMS_PATH):
    SYMPTOMS_DATA_PATH = LOCAL_SYMPTOMS_PATH
else:
    SYMPTOMS_DATA_PATH = REMOTE_SYMPTOMS_PATH

DEFAULT_EXCEL_PATH = SYMPTOMS_DATA_PATH


# Global variable to store the loaded data
_SINTOMAS_TRIAGE: Optional[Dict[str, Dict[str, List[str]]]] = None


@st.cache_data(show_spinner=False)
def load_sintomas_from_excel(
    excel_path: str = DEFAULT_EXCEL_PATH,
    col_categoria: int = 7,
    col_sintoma: int = 8,
    col_modificador: int = 9,
) -> Dict[str, Dict[str, List[str]]]:
    """
    Load triage symptoms data from an Excel file and build nested dictionary.

    This function reads columns from an Excel file and creates a three-level
    hierarchical structure: Category -> Symptom -> Modifiers.

    Parameters
    ----------
    excel_path : str, optional
        Path to the Excel file containing triage data.
        Default is "data/triage_sintomas.xlsx".
    col_categoria : int, optional
        Zero-based column index for categories (default is 7, which is column 8 in Excel).
    col_sintoma : int, optional
        Zero-based column index for symptoms (default is 8, which is column 9 in Excel).
    col_modificador : int, optional
        Zero-based column index for modifiers (default is 9, which is column 10 in Excel).

    Returns
    -------
    dict
        Nested dictionary with structure: {categoria: {sintoma: [modificadores]}}

    Raises
    ------
    FileNotFoundError
        If the Excel file doesn't exist at the specified path.
    ValueError
        If the specified columns don't exist in the Excel file.

    Examples
    --------
    >>> # Load from default location
    >>> data = load_sintomas_from_excel()

    >>> # Load from custom location
    >>> data = load_sintomas_from_excel("custom_path/symptoms.xlsx")

    >>> # Load with different column indices
    >>> data = load_sintomas_from_excel(col_categoria=5, col_sintoma=6, col_modificador=7)
    """
    global _SINTOMAS_TRIAGE

    # Check if file exists (only for local files)
    if not excel_path.startswith("http") and not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    try:
        # Read Excel file
        df = pd.read_excel(excel_path)

        # Validate column indices
        if col_categoria >= len(df.columns):
            raise ValueError(
                f"Column index {col_categoria} is out of range. File has {len(df.columns)} columns."
            )
        if col_sintoma >= len(df.columns):
            raise ValueError(
                f"Column index {col_sintoma} is out of range. File has {len(df.columns)} columns."
            )
        if col_modificador >= len(df.columns):
            raise ValueError(
                f"Column index {col_modificador} is out of range. File has {len(df.columns)} columns."
            )

        # Extract relevant columns
        data_triage = pd.DataFrame(
            {
                "categoria": df.iloc[:, col_categoria],
                "sintoma": df.iloc[:, col_sintoma],
                "modificador": df.iloc[:, col_modificador],
            }
        )

        # Remove rows where all values are NaN
        data_triage = data_triage.dropna(how="all")

        # Build nested dictionary
        sintomas_dict = {}

        for _, row in data_triage.iterrows():
            cat = row["categoria"]
            sint = row["sintoma"]
            mod = row["modificador"]

            # Skip if categoria or sintoma is NaN
            if pd.isna(cat) or pd.isna(sint):
                continue

            # Initialize categoria if not exists
            if cat not in sintomas_dict:
                sintomas_dict[cat] = {}

            # Initialize sintoma if not exists
            if sint not in sintomas_dict[cat]:
                sintomas_dict[cat][sint] = []

            # Add modificador if not NaN and not already in list
            if not pd.isna(mod) and mod not in sintomas_dict[cat][sint]:
                sintomas_dict[cat][sint].append(mod)

        # Update global variable
        _SINTOMAS_TRIAGE = sintomas_dict

        return sintomas_dict

    except Exception as e:
        raise RuntimeError(f"Error loading Excel file '{excel_path}': {str(e)}")


def _get_sintomas_data() -> Dict[str, Dict[str, List[str]]]:
    """
    Get the sintomas data, loading it if necessary.

    Returns
    -------
    dict
        The sintomas triage dictionary.
    """
    global _SINTOMAS_TRIAGE

    if _SINTOMAS_TRIAGE is None:
        load_sintomas_from_excel()

    return _SINTOMAS_TRIAGE


# === Helper Functions ===


def get_categorias():
    """
    Get all available symptom categories.

    Returns
    -------
    list
        A sorted list of all category names.

    Examples
    --------
    >>> categorias = get_categorias()
    >>> print(categorias[0])
    'Boca, garganta y cuello'
    """
    sintomas_triage = _get_sintomas_data()
    return sorted(list(sintomas_triage.keys()))


def get_sintomas(categoria):
    """
    Get all sintomas (symptoms) for a specific category.

    Parameters
    ----------
    categoria : str
        The category name.

    Returns
    -------
    list
        A sorted list of sintoma names for the given category.
        Returns an empty list if the category doesn't exist.

    Examples
    --------
    >>> sintomas = get_sintomas("Boca, garganta y cuello")
    >>> print(sintomas)
    ['Dificultad para tragar (ej: se me atora la comida)', 'Golpe o trauma en la boca']
    """
    sintomas_triage = _get_sintomas_data()
    if categoria not in sintomas_triage:
        return []
    return sorted(list(sintomas_triage[categoria].keys()))


def get_modificadores(categoria, sintoma):
    """
    Get all modificadores (modifiers) for a specific category and sintoma combination.

    Parameters
    ----------
    categoria : str
        The category name.
    sintoma : str
        The sintoma name.

    Returns
    -------
    list
        A list of modificador values for the given category and sintoma.
        Returns an empty list if the combination doesn't exist.

    Examples
    --------
    >>> mods = get_modificadores("Boca, garganta y cuello", "Golpe o trauma en la boca")
    >>> print(len(mods))
    8
    """
    sintomas_triage = _get_sintomas_data()
    if categoria not in sintomas_triage:
        return []
    if sintoma not in sintomas_triage[categoria]:
        return []
    return sintomas_triage[categoria][sintoma]


def get_all_sintomas_flat():
    """
    Get a flattened list of all sintomas across all categories.

    Returns
    -------
    list
        A sorted list of all unique sintoma names.

    Examples
    --------
    >>> all_sintomas = get_all_sintomas_flat()
    >>> print(len(all_sintomas))
    93
    """
    sintomas_triage = _get_sintomas_data()
    sintomas_set = set()
    for categoria in sintomas_triage.values():
        sintomas_set.update(categoria.keys())
    return sorted(list(sintomas_set))


def search_sintomas(keyword):
    """
    Search for sintomas containing a specific keyword (case-insensitive).

    Parameters
    ----------
    keyword : str
        The keyword to search for in sintoma names.

    Returns
    -------
    dict
        A dictionary mapping categories to matching sintomas.
        Format: {categoria: [sintoma1, sintoma2, ...]}

    Examples
    --------
    >>> results = search_sintomas("dolor")
    >>> for cat, sints in results.items():
    ...     print(f"{cat}: {len(sints)} matches")
    """
    sintomas_triage = _get_sintomas_data()
    keyword_lower = keyword.lower()
    results = {}

    for categoria, sintomas in sintomas_triage.items():
        matching_sintomas = [
            sintoma for sintoma in sintomas.keys() if keyword_lower in sintoma.lower()
        ]
        if matching_sintomas:
            results[categoria] = matching_sintomas

    return results


def validate_selection(categoria, sintoma, modificador):
    """
    Validate if a combination of categoria, sintoma, and modificador exists in the data.

    Parameters
    ----------
    categoria : str
        The category name.
    sintoma : str
        The sintoma name.
    modificador : str
        The modificador value.

    Returns
    -------
    bool
        True if the combination exists, False otherwise.

    Examples
    --------
    >>> is_valid = validate_selection(
    ...     "Boca, garganta y cuello",
    ...     "Golpe o trauma en la boca",
    ...     "Ninguno de los anteriores"
    ... )
    >>> print(is_valid)
    True
    """
    sintomas_triage = _get_sintomas_data()
    if categoria not in sintomas_triage:
        return False
    if sintoma not in sintomas_triage[categoria]:
        return False
    return modificador in sintomas_triage[categoria][sintoma]


def get_triage_summary():
    """
    Get a summary of the triage data structure.

    Returns
    -------
    dict
        A dictionary with statistics about the triage data:
        - total_categorias: number of categories
        - total_sintomas: total number of unique sintomas
        - total_modificadores: total number of modificadores across all combinations
        - categorias_detail: list of dicts with details per category

    Examples
    --------
    >>> summary = get_triage_summary()
    >>> print(f"Total categories: {summary['total_categorias']}")
    """
    sintomas_triage = _get_sintomas_data()
    total_modificadores = 0
    categorias_detail = []

    for categoria, sintomas in sintomas_triage.items():
        num_sintomas = len(sintomas)
        num_mods = sum(len(mods) for mods in sintomas.values())
        total_modificadores += num_mods

        categorias_detail.append(
            {
                "categoria": categoria,
                "num_sintomas": num_sintomas,
                "num_modificadores": num_mods,
            }
        )

    return {
        "total_categorias": len(sintomas_triage),
        "total_sintomas": len(get_all_sintomas_flat()),
        "total_modificadores": total_modificadores,
        "categorias_detail": sorted(categorias_detail, key=lambda x: x["categoria"]),
    }


def get_triage_decision(
    categoria: str, sintoma: str, modificador: str, excel_path: str = DEFAULT_EXCEL_PATH
) -> Optional[Dict[str, str]]:
    """
    Get the triage decision (Modalidad, Triage, Especialidad urgencias) for a specific
    combination of categoria, sintoma, and modificador.

    This function searches the Excel file for an exact match of the three parameters
    and returns the corresponding decision values from the same row.

    Parameters
    ----------
    categoria : str
        The symptom category name (e.g., "Boca, garganta y cuello").
    sintoma : str
        The symptom name.
    modificador : str
        The modifier associated with the symptom.
    excel_path : str, optional
        Path to the Excel file. Default is DEFAULT_EXCEL_PATH.

    Returns
    -------
    dict or None
        A dictionary containing the decision values if found:
        {
            "modalidad": str,        # e.g., "Presencial", "Urgencias", "Virtual"
            "triage": str,           # e.g., "T1", "T2", "T3", "T4", "T5"
            "especialidad": str      # e.g., "Odontología", "Medicina interna"
        }
        Returns None if no matching row is found or if the file cannot be read.

    Examples
    --------
    >>> decision = get_triage_decision(
    ...     "Boca, garganta y cuello",
    ...     "Golpe o trauma en la boca",
    ...     "Ninguno de los anteriores"
    ... )
    >>> print(decision)
    {'modalidad': 'Presencial', 'triage': 'T4', 'especialidad': 'Odontología'}

    >>> # Case where no match is found
    >>> decision = get_triage_decision("Categoria invalida", "Sintoma invalido", "Modificador invalido")
    >>> print(decision)
    None
    """
    # Check if file exists (only for local files)
    if not excel_path.startswith("http") and not os.path.exists(excel_path):
        print(f"Error: Excel file not found at {excel_path}")
        return None

    try:
        # Read Excel file
        df = pd.read_excel(excel_path)

        # Column indices (0-based)
        COL_CATEGORIA = 7
        COL_SINTOMA = 8
        COL_MODIFICADOR = 9
        COL_MODALIDAD = 10
        COL_TRIAGE = 13
        COL_ESPECIALIDAD = 17

        # Filter dataframe to find matching row
        mask = (
            (df.iloc[:, COL_CATEGORIA] == categoria)
            & (df.iloc[:, COL_SINTOMA] == sintoma)
            & (df.iloc[:, COL_MODIFICADOR] == modificador)
        )

        matching_rows = df[mask]

        if matching_rows.empty:
            # No matching row found
            return None

        # Get the first matching row
        row = matching_rows.iloc[0]

        # Extract decision values
        modalidad = row.iloc[COL_MODALIDAD]
        triage = row.iloc[COL_TRIAGE]
        especialidad = row.iloc[COL_ESPECIALIDAD]

        # Clean up values (handle NaN and strip whitespace)
        modalidad = str(modalidad).strip() if pd.notna(modalidad) else ""
        triage = str(triage).strip() if pd.notna(triage) else ""
        especialidad = (
            str(especialidad).strip() if pd.notna(especialidad) else "Medicina General"
        )

        return {
            "modalidad": modalidad,
            "triage": triage,
            "especialidad": text_cleaning(especialidad).title(),
        }

    except Exception as e:
        st.error(f"Error reading symptoms file: {str(e)}")
        return None


def build_triage_combinations(excel_path: str) -> pd.DataFrame:
    """
    Build a structured DataFrame of unique triage combinations from the raw triage Excel.

    Reads the full triage symptom matrix and extracts all unique combinations
    of category, symptom, modifier, triage level, modality, and specialty.

    Parameters
    ----------
    excel_path : str
        Path to the triage Excel file (e.g., "data/triage_sintomas.xlsx").

    Returns
    -------
    pd.DataFrame
        Cleaned and normalized DataFrame with columns:
        ['categoria', 'sintoma', 'modificador', 'nivel_triage',
         'modalidad', 'especialidad'].

    Examples
    --------
    >>> df_triage = build_triage_combinations_from_excel("data/triage_sintomas.xlsx")
    >>> df_triage[['nivel_triage', 'especialidad']].head()
    """
    # Read Excel file
    df = pd.read_excel(excel_path)

    # Normalize column names (remove accents and special characters)
    df.columns = (
        df.columns.str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.lower()
        .str.strip()
    )

    # Detect relevant columns automatically
    posibles_cols = df.columns.tolist()
    col_categoria = next((c for c in posibles_cols if "categ" in c), None)
    col_sintoma = next((c for c in posibles_cols if "sintoma" in c), None)
    col_modificador = next((c for c in posibles_cols if "modif" in c), None)
    col_triage = next((c for c in posibles_cols if "triage" in c), None)
    col_modalidad = next((c for c in posibles_cols if "modal" in c), None)
    col_especialidad = next((c for c in posibles_cols if "especial" in c), None)

    if not all(
        [col_categoria, col_sintoma, col_modificador, col_triage, col_modalidad]
    ):
        raise ValueError("No se encontraron todas las columnas necesarias en el Excel.")

    # Filter relevant columns
    columnas_utiles = [
        col_categoria,
        col_sintoma,
        col_modificador,
        col_triage,
        col_modalidad,
        col_especialidad,
    ]
    df_triage = df[columnas_utiles].copy()

    # Normalize text in all columns
    for c in columnas_utiles:
        df_triage[c] = (
            df_triage[c]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
            .str.replace(r"[^a-z0-9\s_]+", "", regex=True)
            .str.replace(r"\s+", "_", regex=True)
        )

    # Remove empty or duplicate rows
    df_triage = df_triage.dropna(subset=[col_categoria, col_sintoma])
    df_triage = df_triage.drop_duplicates().reset_index(drop=True)

    # Rename columns to standard names
    df_triage = df_triage.rename(
        columns={
            col_categoria: "categoria",
            col_sintoma: "sintoma",
            col_modificador: "modificador",
            col_triage: "nivel_triage",
            col_modalidad: "modalidad",
            col_especialidad: "especialidad",
        }
    )

    # Standardize triage level format
    df_triage["nivel_triage"] = df_triage["nivel_triage"].str.upper()
    df_triage["nivel_triage"] = df_triage["nivel_triage"].replace(
        {"1": "T1", "2": "T2", "3": "T3", "4": "T4", "5": "T5"}
    )

    # # Handle missing specialties by assigning 'medicina_general'
    # if "especialidad" in df_triage.columns:
    #     df_triage["especialidad"] = df_triage["especialidad"].replace(
    #         {"nan": "medicina_general"}
    #     )

    return df_triage
