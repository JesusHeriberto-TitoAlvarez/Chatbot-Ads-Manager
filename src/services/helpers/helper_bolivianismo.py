from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_bolivianismo(numero_usuario):
    """
    Genera una respuesta adaptada al uso de bolivianismos relacionados al comercio local,
    utilizando el historial real del usuario como contexto para sonar natural y útil.
    """

    historial_completo = leer_historial(numero_usuario)

    # Extraer últimos mensajes del usuario y del chatbot
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    # DEBUG: mostrar historial que se usará en el prompt
    print("[DEBUG - HISTORIAL BOLIVIANISMO] Mensajes recientes para el prompt:")
    for i, h in enumerate(historial_reciente):
        print(f"[{i}] ({h['role']}) → {h['content']}")

    mensajes = [
        {"role": "system", "content": (
            "El usuario ha utilizado expresiones típicas del español hablado en Bolivia, como 'caserita', 'pahuichi', 'feria', "
            "'almacén', 'boliche' u otras similares, en un contexto relacionado al comercio local o informal.\n\n"
            "INSTRUCCIONES:\n"
            "- Responde con claridad, respeto y cercanía.\n"
            "- Usa un ejemplo sencillo si ayuda, como una tienda de barrio, un negocio en la feria o un pahuichi.\n"
            "- Evita repetir literalmente las expresiones del usuario.\n"
            "- No utilices saludos, ni inicies con frases como 'claro', 'por supuesto' o 'sí te explico'.\n"
            "- Si fluye naturalmente, puedes incluir una expresión boliviana, pero no la fuerces.\n"
            "- El tono debe ser cálido y profesional, sin tecnicismos innecesarios.\n"
            "- No incluyas emojis salvo que aporten claridad."
        )}
    ]

    mensajes.extend(historial_reciente)

    try:
        print("[GPT] Generando respuesta para intención 'bolivianismo'...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=220
        )
        print("[GPT] Respuesta generada exitosamente para intención 'bolivianismo'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_bolivianismo] {e}")
        return (
            "Entiendo que tienes un negocio local y estás buscando formas de promocionarlo. "
            "Google Ads puede ayudarte a que más personas encuentren lo que ofreces, ya sea en tu tienda, feria o incluso en tu pahuichi. "
            "Te puedo guiar paso a paso para crear un anuncio efectivo, sin necesidad de tener experiencia previa."
        )







'''
from src.config import openai_client, GPT_MODEL_GENERAL, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_bolivianismo(numero_usuario):
    """
    Genera una respuesta adaptada al uso de bolivianismos relacionados al comercio local,
    utilizando el historial real del usuario como contexto para sonar natural y útil.
    """

    historial_completo = leer_historial(numero_usuario)

    # Extraer últimos mensajes del usuario y del chatbot
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    mensajes = [
        {"role": "system", "content": (
            "El usuario ha utilizado expresiones típicas del español hablado en Bolivia, como 'caserita', 'pahuichi', 'feria', "
            "'almacén', 'boliche' u otras similares, en un contexto relacionado al comercio local o informal.\n\n"
            "INSTRUCCIONES:\n"
            "- Responde con claridad, respeto y cercanía.\n"
            "- Usa un ejemplo sencillo si ayuda, como una tienda de barrio, un negocio en la feria o un pahuichi.\n"
            "- Evita repetir literalmente las expresiones del usuario.\n"
            "- No utilices saludos, ni inicies con frases como 'claro', 'por supuesto' o 'sí te explico'.\n"
            "- Si fluye naturalmente, puedes incluir una expresión boliviana, pero no la fuerces.\n"
            "- El tono debe ser cálido y profesional, sin tecnicismos innecesarios.\n"
            "- No incluyas emojis salvo que aporten claridad."
        )}
    ]

    mensajes.extend(historial_reciente)

    try:
        print("[GPT] Generando respuesta para intención 'bolivianismo'...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_GENERAL,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=220
        )
        print("[GPT] Respuesta generada exitosamente para intención 'bolivianismo'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_bolivianismo] {e}")
        return (
            "Entiendo que tienes un negocio local y estás buscando formas de promocionarlo. "
            "Google Ads puede ayudarte a que más personas encuentren lo que ofreces, ya sea en tu tienda, feria o incluso en tu pahuichi. "
            "Te puedo guiar paso a paso para crear un anuncio efectivo, sin necesidad de tener experiencia previa."
        )





















from src.config import openai_client, GPT_MODEL_GENERAL, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_bolivianismo(numero_usuario):
    """
    Genera una respuesta adaptada al uso de bolivianismos relacionados al comercio local.
    Utiliza el historial reciente para contextualizar la respuesta.
    """

    historial_completo = leer_historial(numero_usuario)

    # Extraer últimos mensajes del usuario y del chatbot
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    mensajes = [
        {"role": "system", "content": (
            "El usuario ha utilizado expresiones típicas del español hablado en Bolivia, como 'caserita', 'pahuichi', 'feria', "
            "'almacén', 'boliche' u otras similares, especialmente en contexto de comercio informal o negocios locales.\n\n"

            "INSTRUCCIONES:\n"
            "- Redacta una respuesta clara, respetuosa y útil para alguien que quiere mejorar su visibilidad con Google Ads.\n"
            "- No uses un tono exageradamente informal, pero incluye naturalmente una palabra o expresión boliviana si es apropiado.\n"
            "- Sé cálido, directo y útil, como si acompañaras paso a paso a un comerciante boliviano que quiere aprender.\n"
            "- Usa un ejemplo si ayuda, pero no sobrecargues de detalles.\n"
            "- No repitas la expresión que el usuario dijo, solo úsala si fluye con naturalidad.\n"
            "- No incluyas emojis, salvo que aporten claridad. El tono debe ser respetuoso y profesional."
        )}
    ]

    mensajes.extend(historial_reciente)
    mensajes.append({"role": "user", "content": "Estoy buscando cómo hacer publicidad para mi negocio con Google Ads."})

    try:
        print("[GPT] Generando respuesta para intención 'bolivianismo'...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_GENERAL,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=220
        )
        print("[GPT] Respuesta generada exitosamente para intención 'bolivianismo'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_bolivianismo] {e}")
        return (
            "Entiendo que tienes un negocio local y estás buscando formas de promocionarlo. "
            "Google Ads puede ayudarte a que más personas encuentren lo que ofreces, ya sea en tu tienda, feria o incluso en tu pahuichi. "
            "Te puedo guiar paso a paso para crear un anuncio efectivo, sin necesidad de tener experiencia previa."
        )
'''