import pandas as pd
import os
from typing import Dict, List, Optional

# Default path to the triage symptoms Excel file
DEFAULT_EXCEL_PATH = "data/triage_sintomas.xlsx"

# Global variable to store the loaded data
_SINTOMAS_TRIAGE: Optional[Dict[str, Dict[str, List[str]]]] = None


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

    # Check if file exists
    if not os.path.exists(excel_path):
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
