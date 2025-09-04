from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_INTENCIONES
from src.services.helpers.helper_bolivianismo import obtener_respuesta_bolivianismo

def contiene_bolivianismo_comercial(mensaje_usuario):
    """
    Detecta si el mensaje contiene bolivianismos relacionados con el comercio o contexto cultural boliviano.
    Usa GPT para evaluar si el lenguaje usado es típico de Bolivia (feria, caserita, pahuichi, etc.).
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un detector de intenciones culturales. Tu tarea es analizar si el siguiente mensaje del usuario "
            "usa palabras o expresiones características del español hablado en Bolivia, especialmente en contextos de comercio, ferias, "
            "mercados o trato popular. Detecta si aparecen términos como:\n\n"
            "- caserito, caserita\n"
            "- feria, feriante\n"
            "- pahuichi\n"
            "- boliche, bolichero(a)\n"
            "- almacén, almacenero(a), abarrotero(a)\n"
            "- chola, birlocha (como comerciante)\n"
            "- chalona, charque\n"
            "- yapa, vendaje\n"
            "- semillería\n"
            "- chingana\n"
            "- trufi\n"
            "- changuito (cuando es contexto comercial o familiar)\n\n"
            "Responde únicamente con 'sí' o 'no'.\n\n"
            "Ejemplos:\n"
            "Usuario: 'Tengo un pahuichi en El Alto y quiero vender más'\nRespuesta: 'sí'\n"
            "Usuario: '¿Cómo hago publicidad para mi almacén?'\nRespuesta: 'sí'\n"
            "Usuario: 'Vendo chalona y queso en la feria'\nRespuesta: 'sí'\n"
            "Usuario: 'Trabajo en una empresa de tecnología'\nRespuesta: 'no'\n"
            "Usuario: '¿Qué tarjeta necesito para publicar?'\nRespuesta: 'no'\n"
            "Usuario: 'Mi esposa es caserita en la Rodríguez y quiere vender más'\nRespuesta: 'sí'\n"
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
        print(f"[ERROR GPT - intención 'bolivianismo'] No se pudo procesar la intención: {e}")
        return False


def detectar_bolivianismo(mensaje, numero):
    """
    Detecta si hay uso de bolivianismos comerciales y responde con lenguaje adaptado si corresponde.
    """
    if contiene_bolivianismo_comercial(mensaje):
        print(f"[INTENCIÓN ACTIVADA] detectar_bolivianismo → {mensaje}")
        respuesta = obtener_respuesta_bolivianismo(numero)
        return {
            "respuesta": respuesta,
            "inyectar_como": "assistant"
        }
    return None





'''

'''