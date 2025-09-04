from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_que_es_google_ads(numero_usuario):
    """
    Genera una respuesta natural y contextualizada para explicar qué es Google Ads,
    usando el historial reciente del usuario para que la respuesta sea fluida y coherente.
    """

    historial_completo = leer_historial(numero_usuario)

    # Separar mensajes por rol
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    # Fusionar y ordenar cronológicamente
    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    # DEBUG: mostrar historial que GPT usará
    print("[DEBUG - HISTORIAL QUE_ES_GOOGLE_ADS] Mensajes recientes para el prompt:")
    for i, h in enumerate(historial_reciente):
        print(f"[{i}] ({h['role']}) → {h['content']}")

    # Crear el prompt ajustado
    mensajes = [
        {"role": "system", "content": (
            "El usuario quiere saber qué es Google Ads. Tu tarea es explicarlo de forma natural y coherente "
            "con el flujo de conversación actual. No respondas como un robot ni repitas su pregunta.\n\n"

            "INSTRUCCIONES:\n"
            "- Explica qué es Google Ads de forma sencilla y cercana.\n"
            "- Usa ejemplos bolivianos: una pastelería, ferretería o tienda de repuestos en La Paz.\n"
            "- Escribe en frases cortas, claras y cálidas, como si estuvieras en un chat.\n"
            "- No digas 'claro', 'por supuesto' o saludos. Solo responde directo.\n"
            "- Puedes usar un emoji si es útil, pero solo uno.\n"
            "- Máximo 6 líneas visibles en WhatsApp."
        )}
    ]

    mensajes.extend(historial_reciente)

    try:
        print("[GPT] Generando respuesta para intención 'qué es Google Ads' (contextualizada)...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=220
        )
        print("[GPT] Respuesta generada exitosamente para intención 'Google Ads'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_que_es_google_ads] {e}")
        return (
            "Google Ads es una herramienta de Google que te ayuda a promocionar tu negocio en internet. "
            "Por ejemplo, si tienes una ferretería en La Paz, puedes hacer que tu anuncio aparezca cuando alguien busca clavos, cemento o herramientas. "
            "Así más personas encuentran tu negocio fácilmente. 😉"
        )




'''
from src.config import openai_client, GPT_MODEL_GENERAL, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_que_es_google_ads(numero_usuario):
    """
    Genera una respuesta natural y contextualizada para explicar qué es Google Ads,
    usando el historial reciente del usuario para que la respuesta sea fluida y coherente.
    """

    historial_completo = leer_historial(numero_usuario)

    # Separar mensajes por rol
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    # Fusionar y ordenar cronológicamente
    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    # Crear el prompt ajustado
    mensajes = [
        {"role": "system", "content": (
            "El usuario quiere saber qué es Google Ads. Tu tarea es explicarlo de forma natural y coherente "
            "con el flujo de conversación actual. No respondas como un robot ni repitas su pregunta.\n\n"

            "INSTRUCCIONES:\n"
            "- Explica qué es Google Ads de forma sencilla y cercana.\n"
            "- Usa ejemplos bolivianos: una pastelería, ferretería o tienda de repuestos en La Paz.\n"
            "- Escribe en frases cortas, claras y cálidas, como si estuvieras en un chat.\n"
            "- No digas 'claro', 'por supuesto' o saludos. Solo responde directo.\n"
            "- Puedes usar un emoji si es útil, pero solo uno.\n"
            "- Máximo 6 líneas visibles en WhatsApp."
        )}
    ]

    mensajes.extend(historial_reciente)

    try:
        print("[GPT] Generando respuesta para intención 'qué es Google Ads' (contextualizada)...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_GENERAL,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=220
        )
        print("[GPT] Respuesta generada exitosamente para intención 'Google Ads'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_que_es_google_ads] {e}")
        return (
            "Google Ads es una herramienta de Google que te ayuda a promocionar tu negocio en internet. "
            "Por ejemplo, si tienes una ferretería en La Paz, puedes hacer que tu anuncio aparezca cuando alguien busca clavos, cemento o herramientas. "
            "Así más personas encuentran tu negocio fácilmente. 😉"
        )






















from src.config import openai_client, GPT_MODEL_GENERAL, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_que_es_google_ads(numero_usuario):
    """
    Genera una respuesta natural y contextualizada para explicar qué es Google Ads,
    usando historial reciente del usuario y ejemplos locales fáciles de entender.
    """

    historial_completo = leer_historial(numero_usuario)

    # Separar mensajes por rol
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    # Fusionar y ordenar cronológicamente
    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    # Crear el prompt ajustado
    mensajes = [
        {"role": "system", "content": (
            "El usuario acaba de preguntar qué es Google Ads.\n"
            "Tu respuesta debe ser clara, cercana y fácil de entender, como si se lo explicaras por WhatsApp "
            "a alguien que nunca hizo publicidad digital.\n\n"

            "INSTRUCCIONES:\n"
            "- No repitas la pregunta del usuario.\n"
            "- Empieza explicando qué es Google Ads de forma simple.\n"
            "- Incluye un ejemplo concreto y cotidiano, como una tienda de repuestos, una ferretería o una pastelería en La Paz.\n"
            "- Usa frases breves y directas. No más de 6 líneas visuales en WhatsApp.\n"
            "- Si es útil, puedes usar un emoji (solo uno).\n"
            "- No uses tecnicismos ni datos complicados.\n"
            "- Mantén un tono cálido y didáctico, como si estuvieras ayudando a alguien que recién empieza."
        )}
    ]

    mensajes.extend(historial_reciente)
    mensajes.append({"role": "user", "content": "¿Qué es Google Ads?"})

    try:
        print("[GPT] Generando respuesta para intención 'qué es Google Ads'...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_GENERAL,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=220
        )
        print("[GPT] Respuesta generada exitosamente para intención 'Google Ads'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_que_es_google_ads] {e}")
        return (
            "Google Ads es una herramienta de Google que te ayuda a promocionar tu negocio en internet. "
            "Por ejemplo, si tienes una ferretería en La Paz, puedes hacer que tu anuncio aparezca cuando alguien busca clavos, cemento o herramientas. "
            "Así más personas encuentran tu negocio fácilmente. 😉"
'''