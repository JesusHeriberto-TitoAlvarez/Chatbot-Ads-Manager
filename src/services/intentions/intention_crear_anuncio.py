# src/services/intentions/intention_crear_anuncio.py

from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_INTENCIONES
from src.services.helpers.helper_crear_anuncio import iniciar_flujo_creacion_anuncio

def es_intencion_crear_anuncio(mensaje_usuario):
    """
    Esta función determina si el mensaje del usuario indica que quiere crear un anuncio en Google Ads.
    Usa GPT para evaluar la intención y responder con 'sí' o 'no'.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un detector de intenciones. Tu tarea es analizar el siguiente mensaje del usuario y determinar "
            "si expresa su deseo o intención de *crear un anuncio* o *publicitar* en Google Ads. "
            "Debes considerar sinónimos, frases indirectas, errores gramaticales y expresiones locales bolivianas. "
            "Responde únicamente con 'sí' o 'no'.\n\n"
            "Ejemplos:\n"
            "Usuario: 'Quiero hacer un anuncio'\nRespuesta: 'sí'\n"
            "Usuario: 'Deseo anunciar mi negocio'\nRespuesta: 'sí'\n"
            "Usuario: 'Cómo puedo publicitar en Google'\nRespuesta: 'sí'\n"
            "Usuario: 'Ayúdame a crear una publicidad'\nRespuesta: 'sí'\n"
            "Usuario: 'Puedes crear anuncios en Google'\nRespuesta: 'sí'\n"
            "Usuario: 'Puedes crear anuncios por mi'\nRespuesta: 'sí'\n"
            "Usuario: 'Puedes crear campañas en Google'\nRespuesta: 'sí'\n"
            "Usuario: 'Puedes crear campañas por mi'\nRespuesta: 'sí'\n"
            "Usuario: 'Quiero aparecer en Google cuando buscan pastelerías'\nRespuesta: 'sí'\n"
            "Usuario: '¿Qué es Google Ads?'\nRespuesta: 'no'\n"
            "Usuario: '¿Cuánto cuesta?' \nRespuesta: 'no'\n"
            "Usuario: 'Quién te creó?'\nRespuesta: 'no'\n"
            "Ahora analiza el siguiente mensaje del usuario y responde únicamente con 'sí' o 'no'."
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
        print(f"[ERROR GPT - intención 'crear anuncio'] No se pudo procesar la intención: {e}")
        return False


def detectar_crear_anuncio(mensaje, numero):
    """
    Función modular que detecta si el mensaje tiene intención de crear un anuncio.
    Si lo es, activa el flujo respectivo para la creación del anuncio.
    """
    if es_intencion_crear_anuncio(mensaje):
        print(f"[INTENCIÓN ACTIVADA] detectar_crear_anuncio → {mensaje}")
        respuesta = iniciar_flujo_creacion_anuncio(numero)
        return {
            "respuesta": respuesta,
            "inyectar_como": "assistant"
        }
    return None
