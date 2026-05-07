"""
Módulo de Triage con MedGemma.

Reemplaza el árbol de decisión de la v1 por un LLM médico especializado.
MedGemma es el modelo de Google entrenado en datos clínicos — construido
sobre Gemma 3, optimizado para razonamiento médico y triaje.

Flujo:
    texto libre del paciente → MedGemma (HuggingFace API) → T1-T5 + especialidad
"""

import json
import re
import streamlit as st
from huggingface_hub import InferenceClient


# -------------------------------------------------------------------------
# Prompt del sistema — le explica a MedGemma su rol y el formato esperado
# -------------------------------------------------------------------------

SYSTEM_PROMPT = """Eres un asistente de triage médico especializado en el 
sistema de clasificación Manchester Triage System (MTS), adaptado al contexto 
colombiano. Tu rol es analizar síntomas descritos por el paciente y clasificarlos 
en un nivel de triage.

NIVELES DE TRIAGE:
- T1 (Inmediato): Riesgo vital inmediato. Requiere atención en segundos.
  Ejemplos: paro cardíaco, dificultad respiratoria severa, trauma grave.
- T2 (Muy urgente): Riesgo vital potencial. Atención en menos de 15 minutos.
  Ejemplos: dolor torácico intenso, fractura con deformidad, convulsiones.
- T3 (Urgente): Condición urgente pero estable. Atención en menos de 30 minutos.
  Ejemplos: fractura sin deformidad, dolor abdominal moderado, fiebre alta.
- T4 (Menos urgente): Condición no urgente. Atención en menos de 1 hora.
  Ejemplos: dolor leve, infección menor, síntomas crónicos leves.
- T5 (No urgente): Condición electiva. Puede esperar o ir a consulta programada.
  Ejemplos: resfriado común, revisión de resultados, síntomas muy leves.

MODALIDADES:
- Emergencia: Para T1 y T2
- Urgencias: Para T3
- Cita Prioritaria: Para T4
- Cita Programada: Para T5

INSTRUCCIONES:
1. Analiza los síntomas descritos por el paciente
2. Determina el nivel de triage más apropiado
3. Identifica la especialidad médica requerida
4. Responde ÚNICAMENTE con un JSON válido, sin texto adicional

FORMATO DE RESPUESTA (JSON exacto):
{
  "triage": "T1",
  "modalidad": "Emergencia",
  "especialidad": "medicina_general",
  "razonamiento": "Breve explicación clínica en español (máximo 2 oraciones)",
  "signos_alarma": ["signo1", "signo2"]
}

Especialidades válidas: medicina_general, cardiologia, neurologia, ortopedia,
ginecologia, pediatria, psiquiatria, oftalmologia, dermatologia, urologia,
gastroenterologia, neumologia, endocrinologia, traumatologia"""


# -------------------------------------------------------------------------
# Función principal de triage con MedGemma
# -------------------------------------------------------------------------

@st.cache_data(show_spinner=False, ttl=300)
def get_triage_medgemma(
    descripcion_sintomas: str,
    hf_token: str,
    model: str = "google/medgemma-4b-it",
) -> dict:
    """
    Clasifica síntomas usando MedGemma vía HuggingFace Inference API.

    MedGemma es el modelo médico de Google basado en Gemma 3, entrenado
    en datos clínicos incluyendo texto médico, imágenes radiológicas y
    registros de salud electrónicos.

    Parameters
    ----------
    descripcion_sintomas : str
        Descripción libre de síntomas del paciente en español.
    hf_token : str
        Token de HuggingFace con permisos de lectura.
    model : str
        Nombre del modelo en HuggingFace Hub.
        Por defecto usa medgemma-27b-it (27B parámetros, solo texto).

    Returns
    -------
    dict
        {
            "triage": "T1"-"T5",
            "modalidad": str,
            "especialidad": str,
            "razonamiento": str,
            "signos_alarma": list,
            "exito": bool,
            "error": str | None
        }
    """

    # Respuesta de fallback en caso de error
    fallback = {
        "triage": "T3",
        "modalidad": "Urgencias",
        "especialidad": "medicina_general",
        "razonamiento": "Clasificación de respaldo por error en el sistema.",
        "signos_alarma": [],
        "exito": False,
        "error": None,
    }

    if not descripcion_sintomas or len(descripcion_sintomas.strip()) < 10:
        fallback["error"] = "Descripción de síntomas muy corta."
        return fallback

    try:
        # Inicializar cliente de HuggingFace
        client = InferenceClient(
            provider="hf-inference",   # Usa el servidor de inferencia de HF
            api_key=hf_token,
        )

        # Construir el mensaje para el modelo
        # MedGemma usa el formato chat de instrucción (instruction-tuned)
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"Paciente describe sus síntomas:\n\n"
                    f"\"{descripcion_sintomas.strip()}\"\n\n"
                    f"Clasifica el triage y responde SOLO con el JSON."
                ),
            },
        ]

        # Llamada al modelo
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=400,
            temperature=0.1,   # Baja temperatura = respuestas más consistentes
        )

        # Extraer el texto de la respuesta
        raw_text = response.choices[0].message.content.strip()

        # Parsear el JSON de la respuesta
        resultado = _parse_medgemma_response(raw_text)
        resultado["exito"] = True
        resultado["error"] = None
        return resultado

    except Exception as e:
        error_msg = str(e)
        fallback["error"] = error_msg

        # Si es error de autenticación, dar mensaje claro
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            fallback["error"] = (
                "Token de HuggingFace inválido o sin acceso a MedGemma. "
                "Verifica que aceptaste los términos en huggingface.co/google/medgemma-4b-it"
            )
        # Si es error de rate limit
        elif "429" in error_msg or "rate" in error_msg.lower():
            fallback["error"] = (
                "Límite de llamadas alcanzado. Espera unos segundos e intenta de nuevo."
            )

        return fallback


# -------------------------------------------------------------------------
# Función auxiliar — extrae el JSON de la respuesta del modelo
# -------------------------------------------------------------------------

def _parse_medgemma_response(raw_text: str) -> dict:
    """
    Extrae y valida el JSON de la respuesta de MedGemma.

    Los LLMs a veces envuelven el JSON en bloques de código markdown
    (```json ... ```) — esta función los limpia antes de parsear.
    """

    # Intentar extraer JSON de bloques markdown si existen
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
    if json_match:
        raw_text = json_match.group(1)

    # Intentar encontrar JSON directamente en el texto
    json_match2 = re.search(r"\{[\s\S]*\}", raw_text)
    if json_match2:
        raw_text = json_match2.group(0)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        # Si no se puede parsear, retornar estructura por defecto
        return {
            "triage": "T3",
            "modalidad": "Urgencias",
            "especialidad": "medicina_general",
            "razonamiento": "No se pudo interpretar la respuesta del modelo.",
            "signos_alarma": [],
        }

    # Validar y normalizar campos obligatorios
    triage_validos = ["T1", "T2", "T3", "T4", "T5"]
    triage = data.get("triage", "T3")
    if triage not in triage_validos:
        triage = "T3"

    # Calcular modalidad a partir del nivel si no viene en la respuesta
    modalidad_map = {
        "T1": "Emergencia",
        "T2": "Emergencia",
        "T3": "Urgencias",
        "T4": "Cita Prioritaria",
        "T5": "Cita Programada",
    }

    return {
        "triage": triage,
        "modalidad": data.get("modalidad", modalidad_map[triage]),
        "especialidad": data.get("especialidad", "medicina_general"),
        "razonamiento": data.get("razonamiento", ""),
        "signos_alarma": data.get("signos_alarma", []),
    }