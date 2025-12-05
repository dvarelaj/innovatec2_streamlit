import streamlit as st
from typing import Dict, List

# === Colombian Patient Data Constants ===

ID_TYPES = [
    "Cédula de Ciudadanía (CC)",
    "Cédula de Extranjería (CE)",
    "Tarjeta de Identidad (TI)",
    "Pasaporte",
    "Registro Civil (RC)",
    "Permiso Especial de Permanencia (PEP)",
]

SEXO_OPTIONS = ["Masculino", "Femenino"]

"""
Utilidades para cargar y procesar datos de ubicaciones desde proveedores.
"""


# == Location function ==
@st.cache_data(ttl=3600, show_spinner=False)
def get_departamentos_ciudades_from_providers() -> Dict[str, List[str]]:
    """
    Genera el diccionario de departamentos y ciudades desde los datos de proveedores.

    Esta función extrae las ubicaciones únicas de los prestadores de salud
    y las organiza en un diccionario departamento → lista de municipios.

    Returns
    -------
    dict
        Diccionario con estructura {departamento: [ciudad1, ciudad2, ...]}.
        Ambos departamentos y ciudades están ordenados alfabéticamente.

    Examples
    --------
    >>> deptos = get_departamentos_ciudades_from_providers()
    >>> deptos["CUNDINAMARCA"]
    ['BOGOTÁ', 'CHÍA', 'FACATATIVÁ', ...]
    """
    from utils.matching_utils.recommendation_engine import (
        load_and_prepare_provider_data,
    )

    try:
        # Cargar datos de proveedores
        df_prestadores = load_and_prepare_provider_data()

        # Verificar que existan las columnas necesarias
        if (
            "departamento" not in df_prestadores.columns
            or "municipio" not in df_prestadores.columns
        ):
            raise ValueError(
                "Las columnas 'departamento' y 'municipio' no existen en los datos de proveedores"
            )

        # Eliminar valores nulos
        df_clean = df_prestadores[["departamento", "municipio"]].dropna()

        # Agrupar por departamento y obtener ciudades únicas
        departamentos_ciudades = {}

        for departamento in sorted(df_clean["departamento"].unique()):
            ciudades = sorted(
                df_clean[df_clean["departamento"] == departamento]["municipio"]
                .unique()
                .tolist()
            )
            departamentos_ciudades[departamento] = ciudades

        # Validar que haya al menos un departamento
        if not departamentos_ciudades:
            raise ValueError(
                "No se encontraron departamentos en los datos de proveedores"
            )

        return departamentos_ciudades

    except Exception as e:
        # Fallback: retornar diccionario básico con principales ciudades
        st.warning(
            f"⚠️ No se pudieron cargar ubicaciones desde proveedores: Usando ubicaciones por defecto."
        )
        st.expander("Error").write(e)
        return {
            "Antioquia": ["Medellin", "Bello", "Itagui", "Envigado", "Rionegro"],
            "Atlantico": ["Barranquilla", "Soledad", "Malambo", "Sabanalarga"],
            "Bogota D.C.": ["Bogota"],
            "Bolivar": ["Cartagena", "Magangue", "Turbaco"],
            "Boyaca": ["Tunja", "Duitama", "Sogamoso", "Chiquinquira"],
            "Caldas": ["Manizales", "Villamaria", "Chinchina"],
            "Caqueta": ["Florencia", "San Vicente del Caguan"],
            "Casanare": ["Yopal", "Aguazul", "Villanueva"],
            "Cauca": ["Popayan", "Santander de Quilichao", "Puerto Tejada"],
            "Cesar": ["Valledupar", "Aguachica", "Bosconia"],
            "Choco": ["Quibdo", "Istmina", "Acandi"],
            "Cordoba": ["Monteria", "Cerete", "Lorica", "Sahagun"],
            "Cundinamarca": ["Soacha", "Chia", "Zipaquira", "Facatativa", "Girardot"],
            "Huila": ["Neiva", "Pitalito", "Garzon", "La Plata"],
            "La Guajira": ["Riohacha", "Maicao", "Uribia"],
            "Magdalena": ["Santa Marta", "Cienaga", "Fundacion"],
            "Meta": ["Villavicencio", "Acacias", "Granada", "San Martin"],
            "Nariño": ["Pasto", "Tumaco", "Ipiales"],
            "Norte de Santander": ["Cucuta", "Ocaña", "Pamplona", "Villa del Rosario"],
            "Putumayo": ["Mocoa", "Puerto Asis", "Orito"],
            "Quindio": ["Armenia", "Calarca", "Montenegro"],
            "Risaralda": ["Pereira", "Dosquebradas", "Santa Rosa de Cabal"],
            "Santander": ["Bucaramanga", "Floridablanca", "Giron", "Piedecuesta"],
            "Sucre": ["Sincelejo", "Corozal", "San Marcos"],
            "Tolima": ["Ibague", "Espinal", "Melgar", "Honda"],
            "Valle del Cauca": ["Cali", "Palmira", "Buenaventura", "Tulua", "Cartago"],
        }
