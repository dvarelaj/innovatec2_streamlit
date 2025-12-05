"""
Triage-to-service correspondence table builder.

This module constructs the mapping between triage results (level, specialty, modality)
and available healthcare provider services.
"""

import pandas as pd
from utils.matching_utils.semantic_matching import (
    semantic_match_services,
    fuzzy_match_services,
)


def build_correspondence_table(
    df_sintomas: pd.DataFrame,
    df_prestadores: pd.DataFrame,
    special_categories: list[str] = [
        "salud_mental",
        "oftalmologia",
        "riesgo_biologico",
        "neurologico_o_cabeza",
    ],
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
        Must include ['categoria','nivel_triage', 'modalidad', 'especialidad'].
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
        Columns: ['categoria','nivel_triage', 'modalidad_requerida', 'especialidad_requerida',
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
        subset=["categoria", "nivel_triage", "modalidad", "especialidad"]
    ).reset_index(drop=True)

    if verbose:
        print(f"Procesando {len(df_sintomas)} combinaciones únicas de triage...")

    # Main loop: process each triage combination
    for _, row in df_sintomas.iterrows():
        categoria = row["categoria"]
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

        # initialize outputs
        servicios, scores = [], []

        # ===========================================
        # 2️⃣.1️⃣ Match specific categories to services
        # ============================================

        if categoria in special_categories:
            # Use configured matching method
            if method == "semantic":
                servicios, scores = semantic_match_services(
                    categoria,
                    subset["servicio_prestador"].tolist(),
                    threshold=threshold,
                    top_k=top_k,
                )
                tipo = "ctg_semantic_match" if servicios else "sin_match"
            else:
                servicios, scores = fuzzy_match_services(
                    categoria,
                    subset["servicio_prestador"].tolist(),
                    threshold=threshold,
                    top_k=top_k,
                )
                tipo = "ctg_fuzzy_match" if servicios else "sin_match"

        # ============================================
        # 2️⃣.2️⃣ Match specialty to services
        # ===========================================

        if pd.notna(especialidad) and especialidad != "" and not servicios:
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

        # ============================================
        # 3️⃣ Handle no matches and no specialty provided
        # ============================================
        if not servicios:
            if nivel in ["T1", "T2", "T3"]:
                servicios = ["urgencias_medico_general"]
            else:
                servicios = ["consulta_medicina_general"]
            tipo = "fallback"
            scores = [1.0]

        # ============================================
        # 4️⃣ Verbose debug output
        # ============================================
        if verbose:
            print(f"\n[{nivel}] {especialidad} → {tipo}")
            for s, sc in zip(servicios, scores):
                print(f"   ↳ {s} ({sc:.3f})")

        # ============================================
        # 5️⃣  Store result
        # ============================================
        correspondencias.append(
            {
                "categoria": categoria,
                "nivel_triage": nivel,
                "modalidad_requerida": modalidad,
                "especialidad_requerida": especialidad,
                "servicios_sugeridos": servicios,
                "scores": scores,
                "tipo_coincidencia": tipo,
            }
        )

    df_corr = pd.DataFrame(correspondencias)

    return df_corr.drop_duplicates(
        subset=[
            "categoria",
            "nivel_triage",
            "modalidad_requerida",
            "especialidad_requerida",
        ]
    )
