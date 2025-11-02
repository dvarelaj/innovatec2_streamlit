import streamlit as st
import numpy as np
import pandas as pd
from streamlit_folium import st_folium
import folium

from utils.ui_style import general_style_orch

general_style_orch()  # Inject custom styles

st.set_page_config(
    page_title="Recomendador ARL",
    page_icon="🏥",
    layout="wide",  # 'centered' o 'wide'
    initial_sidebar_state="expanded",
)

st.sidebar.markdown("---")

st.sidebar.page_link("pages/1_example.py")

hide_menu_style = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.sidebar.info("")


m = folium.Map(location=[4.65, -74.08], zoom_start=12)
m.add_child(folium.LatLngPopup())  # Allow clicking and obtain coordinates

output = st_folium(m, width=700, height=450)
if output["last_clicked"]:
    st.write("Selected location:", output["last_clicked"])
