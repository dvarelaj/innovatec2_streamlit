import streamlit as st
import numpy as np
import pandas as pd
from streamlit_folium import st_folium

import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, Draw, MeasureControl

from utils.ui_style import general_style_orch
from utils.ui_blocks import menu, fixed_header

general_style_orch()  # Inject custom styles
menu()  # Setup sidebar menu
fixed_header(
    st.session_state.get("nombre_paciente", ""),
    st.session_state.get("gravedad", ""),
    st.session_state.get("ciudad", ""),
)  # Custom fixed header

tabs = st.tabs(["Home", "Form", "Map"])

with tabs[0]:
    st.empty()

with tabs[1]:
    st.empty()

with tabs[2]:
    st.markdown("## Mapa Interactivo")

    m2 = folium.Map(location=[4.65, -74.08], zoom_start=12)
    coords = {
        "Bogotá": [4.65, -74.1],
        "Medellín": [6.25, -75.57],
        "Cali": [3.43, -76.52],
    }
    cluster_ciudades = MarkerCluster(
        name="Ciudades",
    ).add_to(m2)

    for city, coord in coords.items():
        folium.Marker(
            location=coord,
            popup=city,
            tooltip=city,
            icon=folium.Icon(color="red", icon="hospital", prefix="fa"),
        ).add_to(cluster_ciudades)

    # MiniMap().add_to(m2)

    folium.TileLayer(
        "OpenStreetMap",
        name="Mapa #1",
        show=True,
    ).add_to(m2)

    # folium.TileLayer(
    #     "CartoDB positron",
    #     name="Mapa #2",
    #     attr="© OpenStreetMap contributors",
    #     show=False,
    # ).add_to(m2)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri — Source: Esri, DeLorme, NAVTEQ, USGS, and others",
        name="Mapa #2",
        show=False,
    ).add_to(m2)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
        name="Mapa #3",
        show=False,
    ).add_to(m2)

    folium.plugins.LocateControl(auto_start=False).add_to(m2)

    folium.plugins.Fullscreen(
        position="topright",
        title="Expandir",
        title_cancel="Salir",
        force_separate_button=True,
    ).add_to(m2)

    folium.LayerControl().add_to(m2)

    # m2.add_child(folium.plugins.MeasureControl())

    columns = st.columns([1, 8, 1])

    with columns[1]:
        st_folium(m2, width=800, height=500)

st.markdown("___")

# st.markdown(
#     """
# <div style="
#     background-color:#e8f5e9;
#     padding:15px;
#     border-radius:10px;
#     border:1px solid #a5d6a7;
#     text-align:center;">
#     <h3 style='color:#2e7d32;'>✅ Recomendación</h3>
#     <p>El centro médico <b>Clínica del Norte</b> está a solo <b>2.1 km</b>.</p>
# </div>
# """,
#     unsafe_allow_html=True,
# )
