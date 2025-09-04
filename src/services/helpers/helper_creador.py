from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_creador_dinamica(numero_usuario):
    """
    Genera una respuesta conversacional y natural sobre quién creó el chatbot,
    basada en el historial reciente del usuario para mantener coherencia.
    """

    historial_completo = leer_historial(numero_usuario)

    # Separar mensajes por roles
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    # Fusionar y ordenar cronológicamente
    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    # DEBUG: mostrar historial real que usará GPT
    print("[DEBUG - HISTORIAL CREADOR] Mensajes recientes para el prompt:")
    for i, h in enumerate(historial_reciente):
        print(f"[{i}] ({h['role']}) → {h['content']}")

    # Crear el prompt con contexto ajustado y tono cálido
    mensajes = [
        {"role": "system", "content": (
            "El usuario quiere saber quién creó este chatbot. "
            "Tu respuesta debe ser fluida, cálida y coherente con el flujo conversacional reciente.\n\n"
            "INSTRUCCIONES:\n"
            "- No empieces con saludos.\n"
            "- No repitas la pregunta.\n"
            "- No uses frases como 'Claro', 'Sí, te cuento' o 'Por supuesto'.\n"
            "- Deja claro que este chatbot fue creado por Jesús H. Tito A., con el apoyo de Héctor A. Machicado C.\n"
            "- Explica que su objetivo es ayudar a personas con campañas en Google Ads.\n"
            "- Usa lenguaje natural como si estuvieras en un chat real."
        )}
    ]

    mensajes.extend(historial_reciente)

    try:
        print("[GPT] Generando respuesta con información del creador...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=180
        )
        print("[GPT] Respuesta generada exitosamente para intención 'creador'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_creador dinámico] {e}")
        return (
            "Fui creado por Jesús H. Tito A., con el apoyo de Héctor A. Machicado C., "
            "como parte de un proyecto para ayudarte con campañas en Google Ads."
        )




'''
from src.config import openai_client, GPT_MODEL_GENERAL, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_creador_dinamica(numero_usuario):
    """
    Genera una respuesta conversacional y natural sobre quién creó el chatbot,
    basada en el historial reciente del usuario para mantener coherencia.
    """

    historial_completo = leer_historial(numero_usuario)

    # Separar mensajes por roles
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    # Fusionar y ordenar cronológicamente
    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    # Crear el prompt con contexto ajustado y tono cálido
    mensajes = [
        {"role": "system", "content": (
            "El usuario quiere saber quién creó este chatbot. "
            "Tu respuesta debe ser fluida, cálida y coherente con el flujo conversacional reciente.\n\n"
            "INSTRUCCIONES:\n"
            "- No empieces con saludos.\n"
            "- No repitas la pregunta.\n"
            "- No uses frases como 'Claro', 'Sí, te cuento' o 'Por supuesto'.\n"
            "- Deja claro que este chatbot fue creado por Jesús H. Tito A., con el apoyo de Héctor A. Machicado C.\n"
            "- Explica que su objetivo es ayudar a personas con campañas en Google Ads.\n"
            "- Usa lenguaje natural como si estuvieras en un chat real."
        )}
    ]

    mensajes.extend(historial_reciente)

    try:
        print("[GPT] Generando respuesta con información del creador...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_GENERAL,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=180
        )
        print("[GPT] Respuesta generada exitosamente para intención 'creador'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_creador dinámico] {e}")
        return (
            "Fui creado por Jesús H. Tito A., con el apoyo de Héctor A. Machicado C., "
            "como parte de un proyecto para ayudarte con campañas en Google Ads."
        )

























from src.config import openai_client, GPT_MODEL_GENERAL, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_creador_dinamica(numero_usuario):
    """
    Genera una respuesta conversacional y natural sobre quién creó el chatbot.
    Solo se usan las últimas 6 intervenciones del usuario y 6 del chatbot
    para evitar consumir demasiados tokens, sin perder el contexto reciente.
    """

    historial_completo = leer_historial(numero_usuario)

    # Separar mensajes por roles
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    # Fusionar y ordenar cronológicamente
    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    # Crear el prompt con contexto ajustado
    mensajes = [
        {"role": "system", "content": (
            "El usuario acaba de preguntar quién te creó.\n"
            "Tu respuesta debe continuar la conversación de forma natural.\n"
            "No empieces con saludos, ni cambies el tema, ni repitas la pregunta.\n"
            "Tu respuesta debe dejar claro lo siguiente:\n"
            "- Este chatbot es un proyecto desarrollado por *Jesús H. Tito A.*\n"
            "- Contó con el apoyo de *Héctor A. Machicado C.*\n"
            "- El objetivo del proyecto es ayudar a personas como el usuario con campañas en Google Ads.\n"
            "Escríbelo con calidez, de forma cercana y coherente con el flujo de la conversación."
        )}
    ]

    mensajes.extend(historial_reciente)
    mensajes.append({"role": "user", "content": "¿Quién te creó?"})  # Se fuerza la intención

    try:
        print("[GPT] Generando respuesta con información del creador...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_GENERAL,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=180
        )
        print("[GPT] Respuesta generada exitosamente para intención 'creador'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_creador dinámico] {e}")
        return (
            "Fui creado por Jesús H. Tito A., con el apoyo de Héctor A. Machicado C., "
            "como parte de un proyecto para ayudarte con campañas en Google Ads."
        )





from src.config import openai_client, GPT_MODEL_GENERAL, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_creador_dinamica(numero_usuario):
    """
    Genera una respuesta conversacional y natural sobre quién creó el chatbot.

    Solo se usan las últimas 6 intervenciones del usuario y 6 del chatbot
    para evitar consumir demasiados tokens, sin perder el contexto reciente.
    """

    historial_completo = leer_historial(numero_usuario)

    # Separar mensajes por roles
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    # Fusionar y ordenar cronológicamente
    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    # Crear el prompt con contexto ajustado y tono cálido
    mensajes = [
        {"role": "system", "content": (
            "El usuario acaba de preguntar quién creó este chatbot, "
            "y tú debes responder como si ya estuvieras conversando con él. "
            "NO te presentes de nuevo, NO cambies de tema, NO digas saludos como 'hola'. "
            "Tu tarea es dejar claro que fuiste creado por Jesús Tito, "
            "de manera cálida, cercana y fluida, como parte de una charla en curso."
        )}
    ]

    mensajes.extend(historial_reciente)
    mensajes.append({"role": "user", "content": "¿Quién te creó?"})  # Se fuerza la intención

    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_GENERAL,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=150
        )
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_creador dinámico] {e}")
        return "Fui creado por Jesús Tito, quien desarrolló este bot para ayudarte con campañas en Google Ads."
'''