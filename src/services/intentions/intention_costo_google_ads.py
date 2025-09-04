from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_INTENCIONES
from src.services.helpers.helper_costo_google_ads import obtener_respuesta_costo_google_ads

def es_pregunta_sobre_costo_google_ads(mensaje_usuario):
    """
    Esta función determina si el mensaje del usuario está preguntando cuánto cuesta usar Google Ads.
    Usa GPT para evaluar la intención y responder con 'sí' o 'no'.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un detector de intenciones. Tu tarea es analizar el siguiente mensaje del usuario y determinar "
            "si está preguntando por el costo, precio o cuánto se debe pagar para utilizar Google Ads. "
            "Considera variantes como: cuánto cuesta, qué precio tiene, es caro, es costoso, qué se paga, cuánto debo pagar, o cuánto se invierte. "
            "Responde únicamente con 'sí' o 'no'.\n\n"
            "Ejemplos:\n"
            "Usuario: '¿Cuánto cuesta usar Google Ads?'\nRespuesta: 'sí'\n"
            "Usuario: '¿Debo pagar algo para anunciar?'\nRespuesta: 'sí'\n"
            "Usuario: '¿Qué precio tiene Google Ads?'\nRespuesta: 'sí'\n"
            "Usuario: '¿Es muy caro anunciar en Google?'\nRespuesta: 'sí'\n"
            "Usuario: '¿Qué es Google Ads?'\nRespuesta: 'no'\n"
            "Usuario: '¿Quién te creó?'\nRespuesta: 'no'\n"
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
        print(f"[ERROR GPT - intención 'costo google ads'] No se pudo procesar la intención: {e}")
        return False


def detectar_costo_google_ads(mensaje, numero):
    """
    Función modular que detecta si el mensaje es sobre cuánto cuesta Google Ads.
    Si lo es, genera la respuesta dinámica y la retorna para inyectarla.
    """
    if es_pregunta_sobre_costo_google_ads(mensaje):
        print(f"[INTENCIÓN ACTIVADA] detectar_costo_google_ads → {mensaje}")
        respuesta = obtener_respuesta_costo_google_ads(numero)
        return {
            "respuesta": respuesta,
            "inyectar_como": "assistant"
        }
    return None
