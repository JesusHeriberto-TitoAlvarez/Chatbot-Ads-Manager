from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_INTENCIONES
from src.services.helpers.helper_proposito import obtener_respuesta_proposito

def es_pregunta_sobre_proposito(mensaje_usuario):
    """
    Esta función determina si el usuario quiere saber para qué sirve el chatbot,
    cuál es su objetivo o qué puede hacer por él.
    Usa GPT para evaluar la intención y responde con 'sí' o 'no'.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un detector de intenciones. Tu tarea es analizar el siguiente mensaje del usuario y determinar "
            "si está preguntando para qué sirve el chatbot, cuál es su propósito de este chatbot o sistema, qué puede hacer el chatbot o sistema o cómo puede ayudar el chatbot o sistema. "
            "Considera frases como: '¿Para qué sirves?', '¿Cuál es tu propósito?', '¿Qué haces?', '¿En qué me puedes ayudar?', "
            "'no sé qué haces', 'no entiendo tu función'.\n\n"
            "Responde únicamente con 'sí' o 'no'.\n\n"
            "Ejemplos:\n"
            "Usuario: '¿Para qué sirves?'\nRespuesta: 'sí'\n"
            "Usuario: 'Explícame tu función'\nRespuesta: 'sí'\n"
            "Usuario: '¿Qué puedes hacer por mí?'\nRespuesta: 'sí'\n"
            "Usuario: '¿Qué tarjeta necesito para anunciarme?'\nRespuesta: 'no'\n"
            "Usuario: 'Quiero saber más de Google Ads'\nRespuesta: 'no'\n"
            "Ahora analiza el siguiente mensaje."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        response = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=prompt,
            temperature=TEMPERATURA_INTENCIONES,
            max_tokens=3
        )
        respuesta = response.choices[0].message.content.strip().lower()
        return "sí" in respuesta

    except Exception as e:
        print(f"[ERROR GPT - intención 'propósito'] No se pudo procesar la intención: {e}")
        return False


def detectar_proposito(mensaje, numero):
    """
    Función modular que detecta si el mensaje es sobre el propósito del chatbot.
    Si lo es, genera una respuesta cálida explicando su objetivo.
    """
    if es_pregunta_sobre_proposito(mensaje):
        print(f"[INTENCIÓN ACTIVADA] detectar_proposito → {mensaje}")
        respuesta = obtener_respuesta_proposito(numero)
        return {
            "respuesta": respuesta,
            "inyectar_como": "assistant"
        }
    return None
