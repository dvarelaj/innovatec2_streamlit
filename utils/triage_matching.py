"""
Triage-to-service correspondence table builder.

This module constructs the mapping between triage results (level, specialty, modality)
and available healthcare provider services.
"""

import pandas as pd
from utils.semantic_matching import semantic_match_services, fuzzy_match_services


def build_triage_combinations_from_excel(excel_path: str) -> pd.DataFrame:
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

    return df_triage


def build_correspondence_table(
    df_sintomas: pd.DataFrame,
    df_prestadores: pd.DataFrame,
    threshold: float = 0.65,
    top_k: int = 5,
    method: str = "semantic",
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Build a correspondence table between triage results and available provider services.

    This function creates a mapping that suggests appropriate healthcare services
    based on triage level, modality, and specialty requirements.

    Parameters
    ----------
    df_sintomas : pd.DataFrame
        Must include ['nivel_triage', 'modalidad', 'especialidad'].
    df_prestadores : pd.DataFrame
        Must include ['servicio_prestador'] (normalized).
    threshold : float, optional
        Minimum similarity score to consider a valid match (0-1 for semantic, 0-100 for fuzzy).
    top_k : int, optional
        Number of top service matches to return per triage case.
    method : str, optional
        'semantic' (SBERT cosine similarity) or 'fuzzy' (RapidFuzz token sort ratio).
    verbose : bool, optional
        If True, prints progress and intermediate matches.

    Returns
    -------
    pd.DataFrame
        Columns: ['nivel_triage', 'modalidad_requerida', 'especialidad_requerida',
                  'servicios_sugeridos', 'scores', 'tipo_coincidencia']

    Examples
    --------
    >>> df_corr = build_correspondence_table(
    ...     df_triage,
    ...     prestadores_final,
    ...     threshold=0.7,
    ...     top_k=3,
    ...     method="semantic"
    ... )
    """
    correspondencias = []

    # Deduplicate clinical combinations
    df_sintomas = df_sintomas.drop_duplicates(
        subset=["nivel_triage", "modalidad", "especialidad"]
    ).reset_index(drop=True)

    if verbose:
        print(f"Procesando {len(df_sintomas)} combinaciones únicas de triage...")

    # Main loop: process each triage combination
    for _, row in df_sintomas.iterrows():
        nivel = row["nivel_triage"]
        modalidad = row["modalidad"]
        especialidad = str(row["especialidad"]).strip()

        # ============================================
        # 1️⃣ Filter services by triage level
        # ============================================
        if nivel in ["T1", "T2", "T3"]:
            # Emergency/urgent cases
            subset = df_prestadores[
                df_prestadores["servicio_prestador"].str.contains("urgencias", na=False)
            ]
        elif nivel in ["T4", "T5"]:
            # Scheduled consultation cases
            subset = df_prestadores[
                df_prestadores["servicio_prestador"].str.contains("consulta", na=False)
            ]
        else:
            subset = df_prestadores.copy()

        # T1 cases may also need surgery
        if nivel == "T1":
            subset = pd.concat(
                [
                    subset,
                    df_prestadores[
                        df_prestadores["servicio_prestador"].str.contains(
                            "cirugia", na=False
                        )
                    ],
                ]
            ).drop_duplicates(subset=["servicio_prestador"])

        subset = subset.drop_duplicates(subset=["servicio_prestador"])

        # ============================================
        # 2️⃣ Match specialty to services
        # ============================================
        servicios, scores = [], []

        if pd.notna(especialidad) and especialidad != "":
            # Use configured matching method
            if method == "semantic":
                servicios, scores = semantic_match_services(
                    especialidad,
                    subset["servicio_prestador"].tolist(),
                    threshold=threshold,
                    top_k=top_k,
                )
                tipo = "semantic_match" if servicios else "sin_match"
            else:
                servicios, scores = fuzzy_match_services(
                    especialidad,
                    subset["servicio_prestador"].tolist(),
                    threshold=threshold,
                    top_k=top_k,
                )
                tipo = "fuzzy_match" if servicios else "sin_match"
        else:
            # ============================================
            # 3️⃣ Fallback: generic services
            # ============================================
            generic = subset[
                subset["servicio_prestador"].str.contains(
                    "general|no_programada", na=False
                )
            ]
            servicios = list(
                dict.fromkeys(generic["servicio_prestador"].head(top_k).tolist())
            )
            scores = [1.0] * len(servicios)
            tipo = "fallback"

        # ============================================
        # 4️⃣ Handle no matches
        # ============================================
        if not servicios:
            if nivel in ["T1", "T2", "T3"]:
                servicios = ["urgencias_medico_general"]
            else:
                servicios = ["consulta_medicina_general"]
            tipo = "fallback"
            scores = [1.0]

        # ============================================
        # 5️⃣ Verbose debug output
        # ============================================
        if verbose:
            print(f"\n[{nivel}] {especialidad} → {tipo}")
            for s, sc in zip(servicios, scores):
                print(f"   ↳ {s} ({sc:.3f})")

        # ============================================
        # 6️⃣ Store result
        # ============================================
        correspondencias.append(
            {
                "nivel_triage": nivel,
                "modalidad_requerida": modalidad,
                "especialidad_requerida": especialidad or "general",
                "servicios_sugeridos": servicios,
                "scores": scores,
                "tipo_coincidencia": tipo,
            }
        )

    df_corr = pd.DataFrame(correspondencias)
    return df_corr.drop_duplicates(
        subset=["nivel_triage", "modalidad_requerida", "especialidad_requerida"]
    )
