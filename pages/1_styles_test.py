import streamlit as st
from utils.ui_style import general_style_orch
from utils.ui_style import (
    PRIMARY_BLUE,
    SECONDARY_BLUE,
    WHITE,
    DARK_GRAY,
    MID_GRAY,
    YELLOW_ACCENT,
    LIGHT_BLUE,
)
from utils.ui_blocks import menu, fixed_header, options_navigation_horizontal

general_style_orch()  # Inject custom styles
menu()  # Setup sidebar menu
fixed_header(
    st.session_state.get("nombre_paciente", ""),
    st.session_state.get("gravedad", ""),
    st.session_state.get("ciudad", ""),
)  # Custom fixed header

# st.sidebar.info("")

# --- APP TITLE ---
st.title("Style Demo App")
st.write("A sample dashboard to visualize custom Streamlit styles.")

# --- MAIN SECTIONS ---
st.subheader("📄 Text Inputs & Selects")
col1, col2 = st.columns(2)

with col1:
    st.text_input("Enter your name")
    st.text_area("Write a short message")
    st.number_input("Enter a number", min_value=0, max_value=100, value=10)
with col2:
    st.selectbox("Choose an option", ["Option A", "Option B", "Option C"])
    st.multiselect("Select multiple options", ["Python", "SQL", "Streamlit", "Pandas"])
    st.date_input("Pick a date")

# --- BUTTONS ---
st.subheader("🟦 Buttons & Actions")
col_btn1, col_btn2, col_btn3 = st.columns(3)
with col_btn1:
    st.button("Primary Button")
with col_btn2:
    st.download_button(
        "Download File", "Sample text file content", file_name="example.txt"
    )
with col_btn3:
    st.button("Form Submit Button")

# --- SLIDERS & INPUTS ---
st.subheader("🎚️ Sliders and Checkboxes")
col3, col4 = st.columns(2)
with col3:
    st.slider("Select a value", 0, 100, 40)
    st.select_slider("Select a range", options=[0, 25, 50, 75, 100], value=(25, 75))
with col4:
    st.checkbox("Accept Terms and Conditions")
    st.radio("Select one", ["Option 1", "Option 2", "Option 3"])

# --- TABLES & DATAFRAMES ---
st.subheader("📊 Data Display Elements")
import pandas as pd

data = {
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Age": [24, 30, 22, 28],
    "Department": ["HR", "Tech", "Finance", "Marketing"],
}
df = pd.DataFrame(data)
st.dataframe(df)
st.table(df.head(2))

# --- FORM EXAMPLE ---
st.subheader("📝 Example Form")
with st.form("contact_form"):
    st.text_input("Full Name")
    st.text_input("Email Address")
    st.text_area("Message")
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.success("✅ Form submitted successfully!")

# --- CARDS / CONTAINERS ---
st.subheader("📦 Styled Containers")
with st.container():
    st.markdown("### Information Card")
    st.markdown(
        "This container uses a light background and shadow to simulate a card layout."
    )
    st.button("Learn More")

# --- FOOTER NOTE ---
st.markdown("---")
st.caption("© 2025 - Streamlit SURA Style Demo | Designed for UI testing")

st.divider()

import streamlit as st
from streamlit_option_menu import option_menu

# Inicializa el estado de la pestaña
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Inicio"

# Barra de navegación superior
selected = options_navigation_horizontal(
    st.session_state.current_tab,
    PRIMARY_BLUE=PRIMARY_BLUE,
    LIGHT_BLUE=LIGHT_BLUE,
    DARK_GRAY=DARK_GRAY,
    WHITE=WHITE,
)


# Actualiza la pestaña actual al hacer clic
st.session_state.current_tab = selected

# --- CONTENIDO DE CADA SECCIÓN ---
if selected == "Inicio":
    st.title("🏥 Recomendador de Rutas Médicas - ARL Innovetec")
    st.markdown("""
    Bienvenido al asistente de recomendación de puntos de atención médica.  
    Usa el botón siguiente para comenzar con el formulario del paciente.
    """)
    if st.button("➡️ Ir al Formulario"):
        st.session_state.current_tab = "Formulario"
        st.rerun()

# --- FORMULARIO ---
elif selected == "Formulario":
    st.header("🧾 Formulario del Paciente")
    st.session_state["nombre"] = st.text_input(
        "Nombre del paciente", st.session_state.get("nombre", "")
    )
    st.session_state["edad"] = st.number_input(
        "Edad", 0, 120, st.session_state.get("edad", 30)
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Volver al Inicio"):
            st.session_state.current_tab = "Inicio"
            st.rerun()
    with col2:
        if st.button("➡️ Ir al Mapa"):
            st.session_state.current_tab = "Mapa Interactivo"
            st.rerun()

# --- MAPA INTERACTIVO ---
elif selected == "Mapa Interactivo":
    st.header("🗺️ Mapa Interactivo")
    st.markdown("Selecciona tu ubicación para ver los puntos de atención recomendados.")
    st.map()

    cols = st.columns([2, 5, 1])
    with cols[0]:
        if st.button("⬅️ Volver al Formulario"):
            st.session_state.current_tab = "Formulario"
            st.rerun()
    with cols[2]:
        if st.button("🏁 Finalizar"):
            st.success(
                f"¡Gracias, {st.session_state.get('nombre', 'Paciente')}! Se han registrado tus datos correctamente."
            )

st.divider()
