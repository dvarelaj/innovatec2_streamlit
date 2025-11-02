import streamlit as st

st.sidebar.success("Selecciona una página arriba.")

# Título
st.title("Mi primera app con Streamlit 🎈")

# Texto
st.write("¡Hola! Esta es una aplicación hecha con Streamlit.")

# Input de usuario
nombre = st.text_input("¿Cuál es tu nombre?")

# Botón
if st.button("Saludar"):
    st.success(f"Holaaaaa, {nombre}! 👋")

# Slider
edad = st.slider("Selecciona tu edad:", 0, 100, 25)
st.write(f"Tu edad es: {edad}")

# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?", ("Email", "Home phone", "Mobile phone")
)

# Add a slider to the sidebar:
add_slider = st.sidebar.slider("Select a range of values", 0.0, 100.0, (25.0, 75.0))


left_column, right_column = st.columns(2)
# You can use a column just like st.sidebar:
left_column.button("Press me!")

# Or even better, call Streamlit functions inside a "with" block:
with right_column:
    chosen = st.radio(
        "Sorting hat", ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin")
    )
    st.write(f"You are in {chosen} house!")

import time

if st.button("compute"):
    st.write("Starting a long computation...")

    # Add a placeholder
    latest_iteration = st.empty()
    bar = st.progress(0)

    for i in range(100):
        # Update the progress bar with each iteration.
        latest_iteration.text(f"Iteration {i + 1}")
        bar.progress(i + 1)
        time.sleep(0.1)

    latest_iteration.text("...and now we're done!")


with st.form("form_paciente"):
    nombre = st.text_input("Nombre")
    gravedad = st.radio("Gravedad", ["Leve", "Moderada", "Alta"])
    enviado = st.form_submit_button("Buscar puntos de atención")
