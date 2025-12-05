"""
Semantic matching utilities for triage-to-service correspondence.

This module provides functions to match triage results (specialty, triage level)
to available healthcare provider services using either semantic embeddings (SBERT)
or fuzzy string matching (RapidFuzz).
"""

from typing import Tuple, List
import streamlit as st
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import process, fuzz


# Global model cache (lazy loading)
_SEMANTIC_MODEL = None


@st.cache_resource(show_spinner=False)
def load_semantic_model(model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
    """
    Load and cache the sentence transformer model for semantic matching.

    Parameters
    ----------
    model_name : str, optional
        HuggingFace model name for sentence transformers.
        Default: "paraphrase-multilingual-MiniLM-L12-v2"

    Returns
    -------
    SentenceTransformer
        Loaded model ready for encoding.
    """
    global _SEMANTIC_MODEL
    if _SEMANTIC_MODEL is None:
        _SEMANTIC_MODEL = SentenceTransformer(model_name)
    return _SEMANTIC_MODEL


def normalize_text_for_embedding(text: str) -> str:
    """
    Prepare text for semantic embedding models.

    Converts underscores and hyphens to spaces, removes extra spaces,
    and converts to lowercase for better semantic matching.

    Parameters
    ----------
    text : str
        Raw text to normalize.

    Returns
    -------
    str
        Normalized text ready for embedding.

    Examples
    --------
    >>> normalize_text_for_embedding("urgencias_medico_general")
    'urgencias medico general'
    >>> normalize_text_for_embedding("consulta-ortopedista")
    'consulta ortopedista'
    """
    return text.replace("_", " ").replace("-", " ").replace("  ", " ").strip().lower()


def semantic_match_services(
    especialidad: str,
    servicios_disponibles: List[str],
    threshold: float = 0.65,
    top_k: int = 5,
) -> Tuple[List[str], List[float]]:
    """
    Match a specialty to available services using semantic similarity (SBERT).

    Parameters
    ----------
    especialidad : str
        Target specialty to match (e.g., "ortopedia", "neurologia").
    servicios_disponibles : list of str
        Available provider services to match against.
    threshold : float, optional
        Minimum cosine similarity score (0-1) to consider valid match.
    top_k : int, optional
        Maximum number of results to return.

    Returns
    -------
    tuple
        (matched_services, similarity_scores)
        - matched_services: List of service names above threshold
        - similarity_scores: Corresponding similarity scores (0-1)

    Examples
    --------
    >>> services = ["urgencias_ortopedista", "consulta_ortopedista", "urgencias_medico_general"]
    >>> matched, scores = semantic_match_services("ortopedia", services, threshold=0.7)
    >>> print(matched)
    ['urgencias_ortopedista', 'consulta_ortopedista']
    """
    model = load_semantic_model()

    # Encode specialty
    emb_especialidad = model.encode(
        normalize_text_for_embedding(especialidad), convert_to_tensor=True
    )

    # Encode all services
    servicios_clean = [normalize_text_for_embedding(s) for s in servicios_disponibles]
    emb_servicios = model.encode(servicios_clean, convert_to_tensor=True)

    # Compute cosine similarities
    similarities = util.cos_sim(emb_especialidad, emb_servicios)[0]

    # Filter and sort results
    results = [
        (servicios_disponibles[i], float(similarities[i]))
        for i in range(len(similarities))
        if similarities[i] >= threshold
    ]
    results = sorted(results, key=lambda x: x[1], reverse=True)[:top_k]

    # Remove duplicates while preserving order
    servicios = list(dict.fromkeys([r[0] for r in results]))
    scores = [round(r[1], 3) for r in results]

    return servicios, scores


def fuzzy_match_services(
    especialidad: str,
    servicios_disponibles: List[str],
    threshold: float = 0.65,
    top_k: int = 5,
) -> Tuple[List[str], List[float]]:
    """
    Match a specialty to available services using fuzzy string matching.

    Parameters
    ----------
    especialidad : str
        Target specialty to match.
    servicios_disponibles : list of str
        Available provider services to match against.
    threshold : float, optional
        Minimum similarity score (0-1) to consider valid match.
    top_k : int, optional
        Maximum number of results to return.

    Returns
    -------
    tuple
        (matched_services, similarity_scores)
        - matched_services: List of service names above threshold
        - similarity_scores: Corresponding similarity scores (0-1)
    """
    # RapidFuzz returns scores 0-100
    matches = process.extract(
        especialidad,
        servicios_disponibles,
        scorer=fuzz.token_sort_ratio,
        limit=top_k * 2,
    )

    # Filter by threshold and convert to 0-1 scale
    good_matches = [(m[0], m[1]) for m in matches if m[1] >= threshold * 100]
    good_matches = sorted(good_matches, key=lambda x: x[1], reverse=True)[:top_k]

    servicios = list(dict.fromkeys([m[0] for m in good_matches]))
    scores = [round(m[1] / 100, 3) for m in good_matches]

    return servicios, scores
