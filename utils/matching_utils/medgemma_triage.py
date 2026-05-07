"""
Módulo de Triage con MedGemma + Base de Conocimiento HADA/SURA.

MedGemma (Google) analiza síntomas en lenguaje natural usando como
contexto las 85 reglas clínicas del sistema HADA de SURA ARL.
"""

import json
import re
import streamlit as st
from huggingface_hub import InferenceClient


# -------------------------------------------------------------------------
# Base de conocimiento extraída del Excel HADA_ARL
# 15 categorías, 92 síntomas, 85 combinaciones clínicas
# -------------------------------------------------------------------------

KNOWLEDGE_BASE = """
REGLAS DE TRIAGE SISTEMA HADA - SURA ARL
Formato: [NIVEL] Categoría / Síntoma -> Especialidad | Si además: modificadores

[T4] Boca, garganta y cuello / Golpe o trauma en la boca -> Odontología | Si además: Ninguno de los anteriores [T4]; Lesión de encía o mucosas orales [T4]; Cambio de color evidente en un diente luego del trauma [T3]
[T2] Boca, garganta y cuello / Dificultad para tragar (ej: se me atora la comida) -> Medicina interna | Si además: Asociado a trauma o quemadura en el lugar de trabajo [T2]
[T5] Génitourinario / Trauma genital -> Urología | Si además: Ninguno de los anteriores [T5]; Asociado a sangrado o herida abierta en genitales [T2]; Amputación o aplastamiento de genitales [T1]
[T5] Génitourinario / Sensación de masas o abultamiento en región genital posterior a un trauma -> Medicina general | Si además: Ninguno de los anteriores [T5]
[T3] Génitourinario / Sensación de masas o abultamiento en región genital -> Medicina general | Si además: Asociado a dolor intenso o cambios en la coloración de la piel [T3]
[T4] Génitourinario / Secreción de pus por genitales o ano -> Medicina general | Si además: Posterior a procedimiento debido a tu accidente de trabajo o enfermedad laboral [T4]; Posterior a un trauma [T4]; Asociado a fiebre, sudoración, decaimiento o debilidad para pararse Posterior a procedimiento debido a tu accidente de trabajo o enfermedad laboral [T2]
[T4] Génitourinario / Orina con sangre posterior a un trauma -> Urología | Si además: Ninguno de los anteriores [T4]
[T3] Génitourinario / Orina con sangre -> Medicina general | Si además: Fiebre (temperatura mayor a 38° grados medidas por termómetro) debido a procedimiento por evento laboral [T3]; Dolor abdominal fuerte o cólico intenso debido a procedimiento por evento laboral [T3]; Fue producto de un trauma reciente asociado a accidente de trabajo [T3]
[T5] Ginecológico / Secreción o sangrado del pezón -> Ginecología | Si además: Ninguno de los anteriores [T5]; Asociado a trauma [T4]; Asociado a dolor, inflamación, enrojecimiento o calor en la mama [T4]
[T5] Ginecológico / Dolor en senos o mama -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a trauma [T4]; Asociado a dolor, inflamación, enrojecimiento o calor en la mama [T4]
[T4] Ginecológico / Sangrado vaginal -> Medicina general | Si además: Ninguno de los anteriores [T4]; Trauma en zona genital [T3]; Asociado a signos como: sudoración, piel pálida o debilidad para pararse [T2]
[T5] Ginecológico / Flujo vaginal -> Medicina general | Si además: Ninguno de los anteriores [T5]; Posterior a trauma, procedimiento o cirugía reciente asociado a un accidente de trabajo o enfermedad laboral [T4]; Dolor pélvico asociado o no con fiebre (temperatura mayor a 38° grados medidas por termómetro) [T3]
[T5] Ginecológico / Trauma en mama, pecho o tórax -> Ginecología | Si además: Ninguno de los anteriores [T5]; Asociado a deformidad o cambio en el aspecto de la mama [T4]; Asociado a dolor, enrojecimiento, calor, secreción o fiebre [T3]
[T5] Ginecológico / Dolor pélvico o dolor bajito -> Ginecología | Si además: Ninguno de los anteriores [T5]; Posterior a trauma, procedimiento o cirugía reciente por accidente de trabajo o enfermedad laboral [T3]
[T5] Nariz / Alteración del olfato -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a trauma, golpe o caída en el trabajo [T3]; Exposición de sustancias química o irritantes en el trabajo [T4]
[T5] Nariz / Congestión nasal -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a trauma, golpe o caída en el trabajo [T3]; Exposición de sustancias química o irritantes en el trabajo [T4]
[T4] Nariz / Cuerpo extraño en nariz -> Medicina general | Si además: Sin modificador [T4]
[T4] Nariz / Sangrado nasal -> Medicina general | Si además: Ninguno de los anteriores [T4]; Exposición de sustancias química o irritantes en el trabajo [T4]; Posterior a cirugía o procedimiento reciente en cara [T3]
[T4] Nariz / Herida o trauma en nariz -> Medicina general | Si además: Ninguno de los anteriores [T4]; Raspón o herida superficial que presentó sangrado escaso [T4]; Trauma asociado a nariz tapada que dificultad respirar [T3]
[T5] Nariz / Deformidad nasal -> Otorrinolaringología | Si además: Ninguno de los anteriores [T5]; Posterior a procedimiento debido a tu accidente de trabajo [T5]; Asociado a trauma, golpe o caída en el trabajo [T2]
[T5] Neurológico o cabeza / Dolor de cabeza -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a altos niveles de ruido o tensión muscular en tu lugar de trabajo [T4]; Asociado a uso de auriculares de forma constante en tu lugar de trabajo [T4]
[T2] Neurológico o cabeza / Pérdida completa de la movilidad en extremidades (parálisis) -> Medicina general | Si además: Sin modificador [T2]
[T3] Neurológico o cabeza / Parálisis facial o en la cara (ej: boca torcida u ojo cerrado) -> Medicina general | Si además: Sin modificador [T3]
[T5] Neurológico o cabeza / Mareo o vértigo (ej: sensación de movimiento propio o de los objetos) -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a cambios de temperatura en el trabajo [T3]; Asociado sonido fuerte, vibración o trabajos de altura o acuáticos [T4]
[T5] Oídos / Pito en oídos -> Medicina general | Si además: Ninguno de los anteriores [T5]; Luego de exposición a un sonido muy fuerte [T4]; El síntoma fue producto de un trauma en tu lugar de trabajo [T3]
[T4] Neurológico o cabeza / Incapacidad o dificultad para hablar -> Medicina general | Si además: Ninguno de los anteriores [T4]; En tu trabajo tuviste contacto por inhalación, ingesta o manipulación de insumos químicos (ej: pesticidas, disolventes) [T1]; Asociado a trauma, golpe o caída en el trabajo [T1]
[T5] Neurológico o cabeza / Pérdida de la memoria -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a trauma, golpe o caída en el trabajo [T4]; El deterioro de la memoria fue repentino y severo (no sabe quién es, dónde vive o la fecha) [T2]
[T1] Neurológico o cabeza / Tienen convulsiones -> Medicina general | Si además: Sin modificador [T1]
[T1] Neurológico o cabeza / Temblor o movimientos raros en la cara o extremidades -> Medicina general | Si además: Ninguno de los anteriores [T1]; En tu trabajo tuviste contacto por inhalación, ingesta o manipulación de insumos químicos (ej: pesticidas, disolventes) [T1]; Asociado a trauma, golpe o caída en el trabajo [T1]
[T5] Neurológico o cabeza / Alteraciones en el sueño -> Medicina general | Si además: Ninguno de los anteriores [T5]; Tienes antecedentes de depresión o ansiedad [T5]; Posterior a un evento traumático o accidente en tu lugar de trabajo [T5]
[T1] Oftalmología / Trauma severo o penetrante en ojo -> Medicina general | Si además: Sin modificador [T1]
[T3] Oftalmología / Herida en ojo o en párpado -> Medicina general | Si además: Sin modificador [T3]
[T4] Oftalmología / Lagrimeo o secreción constante -> Medicina general | Si además: Ninguno de los anteriores [T4]; Asociado a exposición de sustancias irritantes en tu sitio de trabajo [T4]; Posterior a cirugía en ojos o párpados por accidente de trabajo [T4]
[T5] Oftalmología / Visión borrosa -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a trauma, explosión, golpe o caída en el trabajo [T3]; Asociado a contacto directo de alguna sustancia en el ojo en tu lugar de trabajo [T3]
[T4] Oftalmología / Cuerpo extraño en ojo -> Medicina general | Si además: Ninguno de los anteriores [T4]; Asociado a irritación, dolor, sangrado o secreción en el ojo [T3]; Pérdida o disminución de la visión [T3]
[T5] Oftalmología / Ojo rojo -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a exposición de sustancias irritantes en tu sitio de trabajo [T4]; Asociado a trauma, explosión, golpe o caída en el trabajo [T3]
[T5] Oftalmología / Pérdida total de la visión (ceguera) -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a trauma, explosión, golpe o caída en el trabajo [T2]; Asociado a contacto directo de alguna sustancia en el ojo en tu lugar de trabajo [T2]
[T5] Oftalmología / Disminución de la visión -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a trauma, explosión, golpe o caída en el trabajo [T2]; Asociado a contacto directo de alguna sustancia en el ojo en tu lugar de trabajo [T2]
[T4] Oftalmología / Dolor en el ojo -> Medicina general | Si además: Ninguno de los anteriores [T4]; Asociado a dolor de cabeza secundario a trauma, cirugía o procedimiento médico [T2]; Asociado a trauma, explosión, golpe o caída en el trabajo [T2]
[T5] Oftalmología / Requiero control de mi enfermedad ocular -> Medicina general | Si además: Sin modificador [T5]
[T4] Oídos / Dolor de oído -> Medicina general | Si además: Ninguno de los anteriores [T4]; Luego de exposición a un sonido muy fuerte [T4]; El síntoma fue producto de un trauma en tu lugar de trabajo [T3]
[T5] Oídos / Sensación de oído tapado -> Otorrinolaringología | Si además: Ninguno de los anteriores [T5]; Asociado a cuerpo extraño [T3]; Asociado a uso constante de audífonos o tapones en el lugar de trabajo [T5]
[T5] Oídos / Pérdida o disminución de audición -> Otorrinolaringología | Si además: Ninguno de los anteriores [T5]; Luego de exposición a un sonido muy fuerte [T4]; Asociado a trauma, explosión, golpe o caída en el trabajo [T3]
[T4] Oídos / Cuerpo extraño en oído -> Medicina general | Si además: Sin modificador [T4]
[T4] Oídos / Secreción por el oído -> Medicina general | Si además: Ninguno de los anteriores [T4]; Asociado a uso constante de audífonos o tapones en el lugar de trabajo [T4]; Asociado a trauma, explosión, golpe o caída en el trabajo [T3]
[T3] Oídos / Quemaduras (por calor, vapor, eléctricas o químicas). -> Medicina general | Si además: Sin modificador [T3]
[T4] Oídos / Sangrado por oído el oído -> Medicina general | Si además: Ninguno de los anteriores [T4]; Asociado a trauma, explosión, golpe o caída en el trabajo [T2]; Asociado a cambios de presión o inmersión en tu lugar de trabajo [T3]
[T2] Oídos / Golpe con acumulación de sangre (hematoma) en la oreja -> Medicina general | Si además: Sin modificador [T2]
[T4] Oídos / Tengo ampollas en los oídos -> Medicina general | Si además: Ninguno de los anteriores [T4]; Asociado a quemadura por vapor, líquido, fuego o chispa [T3]; Posterior a quemadura por vapor, líquido, fuego o chispa [T4]
[T5] Muscular o articular / Dolor de espalda -> Medicina general | Si además: Ninguno de los anteriores [T5]; Tengo dolor crónico pero aumentó de forma repentina [T4]; Adormecimiento u hormigueo en las piernas de inicio reciente [T4]
[T5] Muscular o articular / Dolor de cuello -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a trauma, accidente, movimiento brusco, golpe o caída en el trabajo [T3]; Tengo dolor crónico pero aumentó de forma repentina [T4]
[T5] Muscular o articular / Dolor en la rodilla -> Deportologia | Si además: Ninguno de los anteriores [T5]; Calor, enrojecimiento o hinchazón de la rodilla luego de un trauma en el lugar de trabajo [T3]; Asociado a accidente, movimiento brusco, golpe o caída en el trabajo [T3]
[T5] Muscular o articular / Dolor en el hombro -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a accidente, trauma, movimiento brusco, golpe o caída en el trabajo [T3]; Posterior a procedimiento o cirugía a causa de un accidente de trabajo o enfermedad laboral [T4]
[T5] Muscular o articular / Dolor en el tobillo o pie -> Medicina general | Si además: Ninguno de los anteriores [T5]; Calor, enrojecimiento o hinchazón en el tobillo o pie luego de un trauma en el lugar de trabajo [T3]; Asociado a accidente, movimiento brusco, golpe o caída en el trabajo [T3]
[T5] Muscular o articular / Dolor de cadera -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a accidente, trauma, movimiento brusco, golpe o caída en el trabajo [T3]; Posterior a procedimiento o cirugía a causa de un accidente de trabajo o enfermedad laboral [T4]
[T5] Muscular o articular / Dolor en mano o muñeca -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a accidente, trauma, movimiento brusco, golpe o caída en el trabajo [T3]; Posterior a procedimiento o cirugía a causa de un accidente de trabajo o enfermedad laboral [T4]
[T5] Muscular o articular / Dolor en el codo -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a accidente, trauma, movimiento brusco, golpe o caída en el trabajo [T3]; Posterior a procedimiento o cirugía a causa de un accidente de trabajo o enfermedad laboral [T4]
[T4] Muscular o articular / Dolor en extremidades -> Medicina general | Si además: Ninguno de los anteriores [T4]; Hinchazón, enrojecimiento, calor o dolor en una de las extremidades posterior a cirugía o inmovilización por accidente de trabajo o enfermedad laboral [T2]; Hinchazón, enrojecimiento, calor o dolor en una de las extremidades posterior a trauma o quietud prolongada [T2]
[T4] Piel, uñas, cabello, pestañas / Alergia, brote o erupción en la piel -> Medicina general | Si además: Posterior a la manipulación de sustancias químicas o irritantes en el trabajo [T4]; Tengo diagnóstico de dermatitis por causa laboral y requiero control [T5]; Asociado con la ingesta de alimentos suministrados en el trabajo [T4]
[T4] Piel, uñas, cabello, pestañas / Infección en piel -> Dermatología | Si además: Ninguno de los anteriores [T4]; Asociado a trauma o accidente en el lugar de trabajo [T4]; Secundario a procedimiento o cirugía por accidente de trabajo o enfermedad laboral [T3]
[T5] Piel, uñas, cabello, pestañas / Dolor o sensación de quemazón en la piel -> Medicina general | Si además: Ninguno de los anteriores [T5]; Secundario a trauma o amputación de alguna parte de cuerpo por accidente de trabajo [T4]; El dolor no ha mejorado a pesar del uso de analgésicos [T4]
[T4] Piel, uñas, cabello, pestañas / Quemaduras (por calor, exposición al sol, eléctricas o químicas). -> Medicina general | Si además: Ninguno de los anteriores [T4]; Raspón, laceración, abrasión o peladura en la piel secundario a accidente, trauma o golpe en el lugar de trabajo [T4]; Posterior a la manipulación de sustancias químicas o irritantes en el trabajo [T3]
[T5] Piel, uñas, cabello, pestañas / Otros problemas con las uñas -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado al contacto de agentes químicos o sustancias irritantes en el lugar de trabajo [T5]; Desprendimiento de la uña secundario a trauma, golpe, caída o accidente en el lugar de trabajo [T3]
[T4] Piel, uñas, cabello, pestañas / Herida, úlcera o cuerpo extraño en la piel -> Dermatología | Si además: Ninguno de los anteriores [T4]; Posterior a trauma, golpe o accidente en el lugar de trabajo [T3]; Asociado a sangrado o hemorragia que no se detiene [T3]
[T4] Piel, uñas, cabello, pestañas / Lesión en piel de genitales -> Dermatología | Si además: Ninguno de los anteriores [T4]; Asociado a trauma, golpe, caídas o accidente realizando actividades relacionadas con el trabajo [T3]
[T4] Piel, uñas, cabello, pestañas / Mordeduras o picaduras por animales o humanos -> Medicina general | Si además: Ninguno de los anteriores [T4]; Mordedura por culebra o serpiente realizando actividades relacionadas con el trabajo [T2]; Asociado a enrojecimiento, calor, secreción, sangrado escaso o fiebre [T4]
[T4] Piel, uñas, cabello, pestañas / Morado o inflamación posterior a inyección -> Medicina general | Si además: Sin modificador [T4]
[T5] Respiratorio / Tos -> Medicina general | Si además: Ninguno de los anteriores [T5]; Asociado a inhalación de humo, vapores, sustancias químicas o irritantes en el lugar de trabajo [T3]; Antecedente enfermedad respiratoria laboral y ahora con aumento de la tos, dificultad para respirar, flema o cambios en la coloración de esta [T3]
[T3] Respiratorio / Consulta por Covid 19 -> Medicina general | Si además: Tengo antecedente de Covid de origen laboral y ahora presento aumento de la tos, dificultad para respirar, flema o cambios en la coloración de esta [T3]; Tengo antecedente de enfermerad respiratoria laboral y requiero control médico [T5]
[T4] Respiratorio / Dolor o dificultad para respirar -> Medicina general | Si además: Ninguno de los anteriores [T4]; Asociado a golpe, trauma, caída o accidente en el lugar de trabajo [T3]; Asociado a inhalación de humo, vapores, sustancias químicas o irritantes en el lugar de trabajo [T3]
[T2] Respiratorio / Cuerpo extraño en garganta que impide respirar -> Medicina general | Si además: Sin modificador [T2]
[T4] Respiratorio / Sangre al toser -> Medicina general | Si además: Ninguna de las anteriores [T4]; Antecedente enfermedad respiratoria laboral [T3]; Asociado a inhalación de humo, vapores, sustancias químicas o irritantes en el lugar de trabajo [T3]
[T3] Salud mental / Depresión o ansiedad -> Medicina general | Si además: En este momento siento palpitaciones, sudoración, temblor, preocupación excesiva, ideación o intento suicida [T3]; Ya tengo diagnóstico de enfermedad mental de origen enfermedad laboral y se han empeorado los síntomas: llanto frecuente, aislamiento social, inapetencia, alteración del sueño [T5]
[T4] Caídas, accidentes, traumas / Herida por objeto tipo: cuchillo, navaja o machete -> Medicina general | Si además: Ninguno de los anteriores [T4]; Sangrado o hemorragia que no se detiene, realizando actividades relacionadas con el trabajo [T2]; La lesión fue producto de una agresión en el lugar de trabajo [T3]
[T2] Caídas, accidentes, traumas / Herida por arma de fuego, bala o proyectil -> Medicina general | Si además: Sin modificador [T2]
[T4] Caídas, accidentes, traumas / Trauma o golpe en la cabeza -> Medicina general | Si además: Ninguna de las anteriores [T4]; Asociado a pérdida de la conciencia realizando actividades relacionadas con el trabajo [T2]; Asociado a herida en cabeza con exposición o deformidad del hueso [T2]
[T2] Caídas, accidentes, traumas / Aplastamiento, atrapamiento o amputación de una parte del cuerpo -> Medicina general | Si además: Sin modificador [T2]
[T4] Caídas, accidentes, traumas / Trauma en extremidades -> Medicina general | Si además: Ninguna de las anteriores [T4]; Me machuqué un dedo o una parte del cuerpo realizando actividades relacionadas con el trabajo [T4]; Asociado a dolor intenso, deformidad o exposición ósea [T3]
[T4] Caídas, accidentes, traumas / Trauma en tórax o abdomen -> Medicina general | Si además: Ninguna de las anteriores [T4]; Asociado a dificultad para respirar, deformidad en el tórax o tos con sangre [T2]; Asociado a dolor abdominal intenso, morados en el abdomen, vómito, heces u orina con sangre [T2]
[T4] Caídas, accidentes, traumas / Trauma en columna o espalda -> Medicina general | Si además: Ninguna de las anteriores [T4]; Asociado a limitación o incapacidad para mover las extremidades, pérdida de la fuerza o pérdida de la sensibilidad [T2]; Asociado a incontinencia urinaria o fecal [T2]
[T4] Vascular / Ulcera en piel -> Medicina general | Si además: Ninguno de los anteriores [T4]; Relacionado con material quirúrgico o insumos secundario a procedimiento o cirugía por accidente de trabajo o enfermedad laboral [T4]; Asociado a fiebre, dolor, enrojecimiento, salida de pus o calor alrededor de la úlcera [T3]
[T2] Vascular / Dolor en extremidades -> Medicina general | Si además: Hinchazón, enrojecimiento, calor o dolor en una de las extremidades posterior a cirugía o inmovilización por accidente de trabajo o enfermedad laboral [T2]; Hinchazón, enrojecimiento, calor o dolor en una de las extremidades posterior a trauma o quietud prolongada [T2]; Asociado a extremidad fría, morada o azul o sensación de hormigueo, posterior a trauma, cirugía o procedimiento [T2]
[T4] Vascular / Sangrados o hemorragia en extremidades -> Medicina general | Si además: Asociado a herida superficial con sangrado escaso, raspón o laceración [T4]; Asociado a herida con sangrado abundante o con limitación para mover la extremidad [T3]
[T2] Riesgo biológico / Reporte del accidente por primera vez -> Medicina general | Si además: Sin modificador [T2]
[T5] Riesgo biológico / Requiero control -> Medicina general | Si además: Sin modificador [T5]
"""

# -------------------------------------------------------------------------
# Prompt del sistema con conocimiento clínico embebido
# -------------------------------------------------------------------------

SYSTEM_PROMPT = """Eres un asistente de triage médico del sistema HADA de SURA ARL Colombia.
Clasifica síntomas usando el Manchester Triage System adaptado.

NIVELES:
- T1 Inmediato: riesgo vital inmediato (paro, trauma grave, amputación)
- T2 Muy urgente: riesgo potencial, atención <15 min (dolor torácico, convulsiones)
- T3 Urgente: estable pero urgente, <30 min (fractura, dolor moderado, fiebre alta)
- T4 Menos urgente: <1 hora (dolor leve, infección menor)
- T5 No urgente: consulta programada (síntomas leves, seguimiento)

MODALIDADES: T1/T2=Emergencia, T3=Urgencias, T4=Cita Prioritaria, T5=Cita Programada

USA ESTA BASE DE CONOCIMIENTO CLÍNICO DEL SISTEMA HADA:
""" + KNOWLEDGE_BASE + """

INSTRUCCIONES:
1. Analiza los síntomas del paciente
2. Busca la categoría y síntoma más cercano en la base de conocimiento
3. Aplica los modificadores si corresponden
4. Responde ÚNICAMENTE con JSON válido, sin texto adicional

FORMATO DE RESPUESTA:
{
  "triage": "T1",
  "modalidad": "Emergencia",
  "especialidad": "cardiologia",
  "razonamiento": "Explicación clínica breve en español (máx 2 oraciones)",
  "signos_alarma": ["signo1", "signo2"]
}"""


# -------------------------------------------------------------------------
# Función principal
# -------------------------------------------------------------------------

@st.cache_data(show_spinner=False, ttl=300)
def get_triage_medgemma(
    descripcion_sintomas: str,
    hf_token: str,
    model: str = "google/medgemma-4b-it",
) -> dict:
    """
    Clasifica síntomas usando MedGemma 4B con la base de conocimiento HADA.

    Parameters
    ----------
    descripcion_sintomas : str
        Descripción libre de síntomas del paciente.
    hf_token : str
        Token de HuggingFace con permisos de lectura.
    model : str
        Modelo MedGemma a usar. Default: medgemma-4b-it (soportado en hf-inference).

    Returns
    -------
    dict con triage, modalidad, especialidad, razonamiento, signos_alarma, exito, error
    """

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
        fallback["error"] = "Descripción muy corta."
        return fallback

    try:
        client = InferenceClient(
            provider="hf-inference",
            api_key=hf_token,
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Paciente describe sus síntomas:\n\n"
                    f"\"{descripcion_sintomas.strip()}\"\n\n"
                    f"Clasifica el triage usando la base HADA. Responde SOLO con JSON."
                ),
            },
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=400,
            temperature=0.1,
        )

        raw_text = response.choices[0].message.content.strip()
        resultado = _parse_medgemma_response(raw_text)
        resultado["exito"] = True
        resultado["error"] = None
        return resultado

    except Exception as e:
        error_msg = str(e)
        fallback["error"] = error_msg
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            fallback["error"] = "Token de HuggingFace inválido o sin acceso a MedGemma."
        elif "429" in error_msg or "rate" in error_msg.lower():
            fallback["error"] = "Límite de llamadas alcanzado. Espera unos segundos."
        elif "not supported" in error_msg.lower():
            fallback["error"] = f"Modelo no soportado: {error_msg}"
        return fallback


# -------------------------------------------------------------------------
# Parser de respuesta
# -------------------------------------------------------------------------

def _parse_medgemma_response(raw_text: str) -> dict:
    """Extrae y valida el JSON de la respuesta de MedGemma."""

    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
    if json_match:
        raw_text = json_match.group(1)

    json_match2 = re.search(r"\{[\s\S]*\}", raw_text)
    if json_match2:
        raw_text = json_match2.group(0)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "triage": "T3",
            "modalidad": "Urgencias",
            "especialidad": "medicina_general",
            "razonamiento": "No se pudo interpretar la respuesta del modelo.",
            "signos_alarma": [],
        }

    triage_validos = ["T1", "T2", "T3", "T4", "T5"]
    triage = data.get("triage", "T3")
    if triage not in triage_validos:
        triage = "T3"

    modalidad_map = {
        "T1": "Emergencia", "T2": "Emergencia",
        "T3": "Urgencias", "T4": "Cita Prioritaria", "T5": "Cita Programada",
    }

    return {
        "triage": triage,
        "modalidad": data.get("modalidad", modalidad_map[triage]),
        "especialidad": data.get("especialidad", "medicina_general"),
        "razonamiento": data.get("razonamiento", ""),
        "signos_alarma": data.get("signos_alarma", []),
    }