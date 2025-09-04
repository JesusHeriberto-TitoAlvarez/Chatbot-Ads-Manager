from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_INTENCIONES
from src.services.helpers.helper_creador import obtener_respuesta_creador_dinamica

def es_pregunta_sobre_creador(mensaje_usuario):
    """
    Esta función determina si el mensaje del usuario es una pregunta sobre quién creó el chatbot.

    Usa GPT para interpretar la intención del mensaje.
    No importa si el usuario escribe: "¿Quién te creó?", "¿Quién te hizo?" o "¿Quién te programó?",
    GPT evaluará la intención y responderá 'sí' o 'no'.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un detector de intenciones. Tu tarea es analizar el siguiente mensaje del usuario y determinar "
            "si está preguntando sobre el creador, diseñador, programador, desarrollador, inventor, autor o cualquier persona que haya construido este chatbot. "
            "También considera formas informales como: papá del bot, hacedor, quien lo hizo, quien lo montó, o dueño del chatbot. "
            "Responde únicamente con 'sí' o 'no'.\n\n"
            "Ejemplos:\n"
            "Usuario: '¿Quién te creó?'\nRespuesta: 'sí'\n"
            "Usuario: '¿Quién es tu papá?'\nRespuesta: 'sí'\n"
            "Usuario: '¿Quién fue tu hacedor?'\nRespuesta: 'sí'\n"
            "Usuario: '¿Quién te montó?'\nRespuesta: 'sí'\n"
            "Usuario: '¿Cómo funciona Google Ads?'\nRespuesta: 'no'\n"
            "Usuario: '¿Qué presupuesto necesito para una campaña?'\nRespuesta: 'no'\n"
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
        print(f"[ERROR GPT - intención 'creador'] No se pudo procesar la intención: {e}")
        return False


def detectar_creador(mensaje, numero):
    """
    Función modular que detecta si el mensaje es sobre el creador del bot.
    Si lo es, genera la respuesta dinámica y la retorna para inyectarla.
    """
    if es_pregunta_sobre_creador(mensaje):
        print(f"[INTENCIÓN ACTIVADA] detectar_creador → {mensaje}")
        respuesta = obtener_respuesta_creador_dinamica(numero)
        return {
            "respuesta": respuesta,
            "inyectar_como": "assistant"
        }
    return None



'''
from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_INTENCIONES
from src.services.helpers.helper_creador import obtener_respuesta_creador_dinamica

def es_pregunta_sobre_creador(mensaje_usuario):
    """
    Esta función determina si el mensaje del usuario es una pregunta sobre quién creó el chatbot.

    Usa GPT para interpretar la intención del mensaje.
    No importa si el usuario escribe: "¿Quién te creó?", "¿Quién te hizo?" o "¿Quién te programó?",
    GPT evaluará la intención y responderá 'sí' o 'no'.
    """

    # Prompt simple para que GPT responda solamente con "sí" o "no"
    prompt = [
        {"role": "system", "content": (
            "Tu tarea es responder únicamente con 'sí' o 'no'.\n"
            "Debes analizar si el siguiente mensaje del usuario es una pregunta sobre quién creó, diseñó o desarrolló este chatbot."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        # Llamamos a GPT con el modelo preciso (1106) y temperatura baja
        response = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,  # gpt-3.5-turbo-1106
            messages=prompt,
            temperature=TEMPERATURA_INTENCIONES,  # Recomendado: 0.2
            max_tokens=3  # Solo esperamos una respuesta corta ("sí" o "no")
        )

        # Limpieza y verificación de la respuesta
        respuesta = response.choices[0].message.content.strip().lower()
        return "sí" in respuesta

    except Exception as e:
        print(f"[ERROR GPT - intención 'creador'] No se pudo procesar la intención: {e}")
        return False  # Si falla algo, asumimos que no es la intención buscada


def detectar_creador(mensaje, numero):
    """
    Función modular que detecta si el mensaje es sobre el creador del bot.
    Si lo es, genera la respuesta dinámica y la retorna para inyectarla.
    """
    if es_pregunta_sobre_creador(mensaje):
        respuesta = obtener_respuesta_creador_dinamica(numero)
        return {
            "respuesta": respuesta,
            "inyectar_como": "assistant"
        }
    return None
'''