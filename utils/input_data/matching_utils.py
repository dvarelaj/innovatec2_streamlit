import streamlit as st
from sentence_transformers import SentenceTransformer
from rapidfuzz import process, fuzz


@st.cache_resource
def load_semantic_model():
    return SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
