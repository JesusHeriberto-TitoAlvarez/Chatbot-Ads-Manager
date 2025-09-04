from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_INTENCIONES
from src.services.helpers.helper_que_es_google_ads import obtener_respuesta_que_es_google_ads

def es_pregunta_sobre_google_ads(mensaje_usuario):
    """
    Esta función determina si el mensaje del usuario está preguntando qué es Google Ads.
    Usa GPT para evaluar la intención y responder con 'sí' o 'no'.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un detector de intenciones. Tu tarea es analizar el siguiente mensaje del usuario y determinar "
            "si está preguntando qué es Google Ads o solicita una explicación básica sobre esta plataforma publicitaria. "
            "Considera variantes como: qué es google ads, cómo funciona google ads, para qué sirve google ads o si alguien quiere que se lo expliques respecto a google ads. "
            "Responde únicamente con 'sí' o 'no'.\n\n"
            "Ejemplos:\n"
            "Usuario: '¿Qué es Google Ads?'\nRespuesta: 'sí'\n"
            "Usuario: 'Explícame cómo funciona Google Ads'\nRespuesta: 'sí'\n"
            "Usuario: 'Para qué sirve Google Ads'\nRespuesta: 'sí'\n"
            "Usuario: '¿Quién te creó?'\nRespuesta: 'no'\n"
            "Usuario: '¿Qué tarjeta necesito?'\nRespuesta: 'no'\n"
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
        print(f"[ERROR GPT - intención 'google ads'] No se pudo procesar la intención: {e}")
        return False


def detectar_que_es_google_ads(mensaje, numero):
    """
    Función modular que detecta si el mensaje es sobre qué es Google Ads.
    Si lo es, genera la respuesta dinámica y la retorna para inyectarla.
    """
    if es_pregunta_sobre_google_ads(mensaje):
        print(f"[INTENCIÓN ACTIVADA] detectar_que_es_google_ads → {mensaje}")
        respuesta = obtener_respuesta_que_es_google_ads(numero)
        return {
            "respuesta": respuesta,
            "inyectar_como": "assistant"
        }
    return None





'''
from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_INTENCIONES
from src.services.helpers.helper_que_es_google_ads import obtener_respuesta_que_es_google_ads

def es_pregunta_sobre_google_ads(mensaje_usuario):
    """
    Esta función determina si el mensaje del usuario está preguntando qué es Google Ads.
    Usa GPT para evaluar la intención y responder con 'sí' o 'no'.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un detector de intenciones. Tu tarea es analizar el siguiente mensaje del usuario y determinar "
            "si está preguntando qué es Google Ads o solicita una explicación básica sobre esta plataforma publicitaria. "
            "Considera variantes como: qué es, cómo funciona, para qué sirve o si alguien quiere que se lo expliques. "
            "Responde únicamente con 'sí' o 'no'.\n\n"
            "Ejemplos:\n"
            "Usuario: '¿Qué es Google Ads?'\nRespuesta: 'sí'\n"
            "Usuario: 'Explícame cómo funciona Google Ads'\nRespuesta: 'sí'\n"
            "Usuario: 'Para qué sirve Google Ads'\nRespuesta: 'sí'\n"
            "Usuario: '¿Quién te creó?'\nRespuesta: 'no'\n"
            "Usuario: '¿Qué tarjeta necesito?'\nRespuesta: 'no'\n"
            "Ahora analiza el siguiente mensaje."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        response = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_INTENCIONES,
            max_tokens=3
        )
        respuesta = response.choices[0].message.content.strip().lower()
        return "sí" in respuesta

    except Exception as e:
        print(f"[ERROR GPT - intención 'google ads'] No se pudo procesar la intención: {e}")
        return False


def detectar_que_es_google_ads(mensaje, numero):
    """
    Función modular que detecta si el mensaje es sobre qué es Google Ads.
    Si lo es, genera la respuesta dinámica y la retorna para inyectarla.
    """
    if es_pregunta_sobre_google_ads(mensaje):
        print(f"[INTENCIÓN ACTIVADA] detectar_que_es_google_ads → {mensaje}")
        respuesta = obtener_respuesta_google_ads(numero)
        return {
            "respuesta": respuesta,
            "inyectar_como": "assistant"
        }
    return None
'''