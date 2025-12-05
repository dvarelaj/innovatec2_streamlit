"""
Utilidades de debugging para el sistema de recomendación.

Este módulo proporciona funciones para mostrar información técnica
del pipeline de recomendación en formato de debug.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any


def show_recommendation_debug_info(
    categoria: str,
    nivel_triage: str,
    especialidad: str,
    user_dept: str,
    user_city: str,
    user_location: Dict,
    df_correspondencia: pd.DataFrame,
    servicios_recomendados: List[str],
    scores: List[float],
    tipo_match: str,
    df_prestadores: pd.DataFrame,
    providers_filtered: pd.DataFrame,
    expanded: bool = False,
):
    """
    Muestra un panel consolidado de información técnica del sistema de recomendación.

    Parameters
    ----------
    categoria : str
        Categoría de síntoma seleccionada.
    nivel_triage : str
        Nivel de triage (T1-T5).
    especialidad : str
        Especialidad requerida.
    user_dept : str
        Departamento del usuario.
    user_city : str
        Municipio del usuario.
    user_location : dict
        Coordenadas del usuario {"lat": float, "lng": float}.
    df_correspondencia : pd.DataFrame
        Tabla de correspondencia triage→servicios.
    servicios_recomendados : list of str
        Servicios sugeridos por el sistema.
    scores : list of float
        Puntajes de confianza.
    tipo_match : str
        Tipo de coincidencia (semantic, fuzzy, fallback).
    df_prestadores : pd.DataFrame
        Dataset completo de prestadores.
    providers_filtered : pd.DataFrame
        Prestadores filtrados por servicio y ubicación.
    expanded : bool, optional
        Si el expander debe estar expandido por defecto (default: False).
    """
    with st.expander("🔍 DEBUG: Información técnica del sistema", expanded=expanded):
        # Sección 1: Datos de entrada
        st.markdown("### 1️⃣ Datos de entrada")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Categoría:**", categoria)
            st.write("**Nivel de triage:**", nivel_triage)
            st.write("**Especialidad:**", especialidad)
        with col2:
            st.write("**Departamento:**", user_dept)
            st.write("**Municipio:**", user_city)
            st.write("**Ubicación usuario:**", user_location)

        # Sección 2: Tabla de correspondencia
        st.markdown("---")
        st.markdown("### 2️⃣ Tabla de correspondencia")
        st.write(f"**Total de filas:** {len(df_correspondencia)}")
        st.write("**Columnas:**", list(df_correspondencia.columns))
        st.dataframe(df_correspondencia.head(30), use_container_width=True)

        # Sección 3: Recomendación obtenida
        st.markdown("---")
        st.markdown("### 3️⃣ Recomendación obtenida")
        st.write("**Servicios recomendados:**", servicios_recomendados)
        st.write("**Scores:**", scores)
        st.write("**Tipo de match:**", tipo_match)

        # Sección 4: Datos de prestadores
        st.markdown("---")
        st.markdown("### 4️⃣ Datos de prestadores cargados")
        st.write(f"**Total prestadores:** {len(df_prestadores)}")
        st.write(
            "**Servicios únicos:**", df_prestadores["servicio_prestador"].nunique()
        )
        st.write("**Top 10 servicios más comunes:**")
        st.dataframe(
            df_prestadores["servicio_prestador"].value_counts().head(10),
            use_container_width=True,
        )

        # Sección 5: Resultado del filtrado
        st.markdown("---")
        st.markdown("### 5️⃣ Resultado del filtrado")
        st.write(f"**Prestadores filtrados:** {len(providers_filtered)}")
        if len(providers_filtered) > 0:
            st.write("**Columnas del resultado:**", list(providers_filtered.columns))
            st.dataframe(providers_filtered.head(10), use_container_width=True)
        else:
            st.warning("No se encontraron prestadores después del filtrado")
            st.write("**Verificando disponibilidad de servicios en dataset completo:**")
            for servicio in servicios_recomendados:
                count = len(
                    df_prestadores[df_prestadores["servicio_prestador"] == servicio]
                )
                st.write(f"  - {servicio}: {count} prestadores")
