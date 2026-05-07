import re

# Leer el archivo original
with open('utils/ui_blocks.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Nueva función symptoms_form con MedGemma
nueva_funcion = '''def symptoms_form():
    """
    Formulario de síntomas con MedGemma.
    Reemplaza los 3 dropdowns del árbol de decisión (v1) por un campo
    de texto libre analizado por MedGemma.
    """
    from utils.matching_utils.medgemma_triage import get_triage_medgemma

    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
            border-left: 4px solid #43a047;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 18px;
        ">
        <b>🤖 Triage asistido por MedGemma</b><br>
        <span style="font-size:0.9rem">
        Describa sus síntomas con sus propias palabras. El modelo médico
        MedGemma analizará su descripción y determinará el nivel de triage.
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    descripcion = st.text_area(
        "Describa sus síntomas actuales:",
        placeholder=(
            "Ejemplo: Tengo dolor en el pecho desde hace 2 horas, "
            "me falta el aire cuando camino y siento palpitaciones. "
            "También tengo el brazo izquierdo dormido."
        ),
        height=140,
        key="descripcion_sintomas",
        help="Sea lo más específico posible: dónde duele, desde cuándo, qué tan intenso.",
    )

    st.caption(
        "💡 Incluya: localización del síntoma, tiempo de evolución, "
        "intensidad (1-10) y síntomas acompañantes."
    )

    analizar = st.button(
        "🔬 Analizar síntomas con MedGemma",
        use_container_width=True,
        type="primary",
    )

    if analizar:
        if not descripcion or len(descripcion.strip()) < 20:
            st.warning(
                "⚠️ Por favor describa sus síntomas con más detalle "
                "(mínimo 20 caracteres)."
            )
            return False

        hf_token = st.secrets.get("HF_TOKEN", "")
        if not hf_token:
            st.error(
                "❌ Token de HuggingFace no configurado. "
                "Verifique el archivo .streamlit/secrets.toml"
            )
            return False

        with st.spinner("🧠 MedGemma analizando síntomas..."):
            resultado = get_triage_medgemma(
                descripcion_sintomas=descripcion,
                hf_token=hf_token,
            )

        st.session_state["decision_triage"] = resultado["triage"]
        st.session_state["decision_modalidad"] = resultado["modalidad"]
        st.session_state["decision_especialidad"] = resultado["especialidad"]
        st.session_state["selected_categoria"] = resultado["especialidad"]
        st.session_state["selected_sintoma"] = descripcion[:50]
        st.session_state["selected_modificador"] = "medgemma"
        st.session_state["form_symptoms_completed"] = True

        if resultado["exito"]:
            nivel = resultado["triage"]
            color_map = {
                "T1": "#d32f2f", "T2": "#e64a19",
                "T3": "#f57c00", "T4": "#388e3c", "T5": "#1976d2",
            }
            color = color_map.get(nivel, "#757575")

            st.markdown(
                f"""
                <div style="
                    border: 2px solid {color};
                    border-radius: 10px;
                    padding: 16px;
                    margin-top: 12px;
                ">
                <h4 style="color:{color}; margin:0">
                    Nivel {nivel} — {resultado['modalidad']}
                </h4>
                <p style="margin: 8px 0 4px">
                    <b>Especialidad:</b> {resultado['especialidad'].replace('_', ' ').title()}
                </p>
                <p style="margin: 4px 0; font-size: 0.9rem; color: #555">
                    <b>Razonamiento clínico:</b> {resultado['razonamiento']}
                </p>
                """,
                unsafe_allow_html=True,
            )

            if resultado.get("signos_alarma"):
                st.markdown(
                    "⚠️ **Signos de alarma identificados:** "
                    + ", ".join(resultado["signos_alarma"])
                )

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.warning(
                f"⚠️ MedGemma no disponible. Se usó clasificación de respaldo. "
                f"Error: {resultado.get('error', 'desconocido')}"
            )

    return st.session_state.get("form_symptoms_completed", False)

'''

# Reemplazar la función usando regex
# Captura desde "def symptoms_form" hasta "def display_triage_result"
patron = r'def symptoms_form\(.*?(?=\ndef display_triage_result)'
nuevo_content = re.sub(patron, nueva_funcion, content, flags=re.DOTALL)

# Verificar que el reemplazo funcionó
if 'MedGemma' in nuevo_content:
    with open('utils/ui_blocks.py', 'w', encoding='utf-8') as f:
        f.write(nuevo_content)
    print("✅ Reemplazo exitoso - MedGemma integrado en ui_blocks.py")
else:
    print("❌ Error: el reemplazo no funcionó")