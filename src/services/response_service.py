from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_CONVERSACION

def generar_respuesta(mensaje_usuario, numero, historial):
    print("[GPT] Generando respuesta personalizada...")

    # Extraer solo los últimos 6 mensajes útiles para el historial resumido
    historial_resumido = historial[-6:] if len(historial) > 6 else historial

    # 🔍 LOG TEMPORAL: ver el historial que se usará
    print("[DEBUG] Historial resumido usado en el system prompt:")
    for i, h in enumerate(historial_resumido):
        print(f"[{i}] ({h.get('role')}) → {h.get('content')}")

    mensaje_system = (
        "Eres Chatbot Ads Manager, un guía conversacional que ayuda a personas sin experiencia a comprender y aprovechar la publicidad digital, "
        "en especial a través de Google Ads. Tu rol es acompañar al usuario con explicaciones simples, ejemplos prácticos y pasos concretos, "
        "como si fueras alguien de confianza que le enseña con calma y buena onda.\n\n"
        
        f"Estás interactuando con un usuario mediante un historial como este: {historial_resumido}.\n\n"
        
        "- Responde siempre con naturalidad, como si conversaras por WhatsApp.\n"
        "- Si te saludan, responde con un saludo breve y cálido.\n"
        "- Si te hacen una pregunta o te dan una instrucción, responde directo al tema, con amabilidad.\n"
        "- No digas frases como 'soy un asistente' o 'fui creado para ayudarte', a menos que te lo pregunten.\n"
        "- Usa explicaciones breves, humanas y útiles. Máximo 150 palabras y 6 líneas de WhatsApp.\n"
        "- Puedes incluir listas cortas o ejemplos si ayudan a entender mejor.\n"
        "- Menciona las ventajas reales de Google Ads cuando sea útil, usando lenguaje claro y adaptado a negocios bolivianos.\n"
        "- Usa emojis con moderación (máximo uno), solo si aportan cercanía o confianza.\n"
        "- Nunca uses más de una exclamación seguida.\n"
        "- Siempre responde en el idioma del usuario, con naturalidad y buena onda."
    )


    mensajes = [{"role": "system", "content": mensaje_system}]

    historial_filtrado = [
        mensaje for mensaje in historial
        if isinstance(mensaje, dict)
        and "role" in mensaje
        and "content" in mensaje
    ]
    mensajes.extend(historial_filtrado)

    try:
        response = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=500
        )

        respuesta = response.choices[0].message.content.strip()
        print("[GPT] Respuesta generada exitosamente.")
        return respuesta

    except Exception as e:
        print(f"[ERROR GPT] No se pudo generar la respuesta: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. ¿Podés intentar de nuevo?"





'''
CODIGO MUY FUNCIONAL
from src.config import openai_client, GPT_MODEL, TEMPERATURA_CONVERSACION

def generar_respuesta(mensaje_usuario, numero, historial):
    print("[GPT] Generando respuesta personalizada...")

    # Extraer solo los últimos 6 mensajes útiles para el historial resumido
    historial_resumido = historial[-6:] if len(historial) > 6 else historial

    mensaje_system = (
        "Eres Chatbot Ads Manager, un asistente inteligente que ayuda a personas sin experiencia a usar Google Ads. "
        f"Estás interactuando con un usuario mediante un historial como este: {historial_resumido}. "
        "Lo más importante es que tus respuestas deben sonar lo más naturales posible, como si estuvieras conversando por WhatsApp.\n\n"
        "- Si el usuario te saluda, puedes devolver un saludo breve.\n"
        "- Si el usuario hace una pregunta o te da una instrucción, responde directo al tema con amabilidad.\n"
        "- No digas frases como 'soy un asistente' o 'fui creado para ayudarte', a menos que te lo pregunten explícitamente.\n"
        "- Tus respuestas deben ser cálidas, útiles, breves y humanas.\n"
        "- Escribe un solo bloque de texto, con máximo 150 palabras y 6 líneas de WhatsApp.\n"
        "- Puedes usar listas o ejemplos si ayudan a explicar mejor.\n"
        "- Usa emojis con moderación, solo si aportan cercanía o buena onda. No más de uno por respuesta.\n"
        "- Nunca uses más de una exclamación seguida.\n"
        "- Siempre responde en el idioma del usuario, con naturalidad."
    )

    mensajes = [{"role": "system", "content": mensaje_system}]

    historial_filtrado = [
        mensaje for mensaje in historial
        if isinstance(mensaje, dict)
        and "role" in mensaje
        and "content" in mensaje
    ]
    mensajes.extend(historial_filtrado)

    try:
        response = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=500
        )

        respuesta = response.choices[0].message.content.strip()
        print("[GPT] Respuesta generada exitosamente.")
        return respuesta

    except Exception as e:
        print(f"[ERROR GPT] No se pudo generar la respuesta: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. ¿Podés intentar de nuevo?"


















from src.config import openai_client, GPT_MODEL, GPT_MODEL_GENERAL, TEMPERATURA_CONVERSACION

def es_saludo_gpt(mensaje_usuario):
    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_GENERAL,
            messages=[
                {"role": "system", "content": (
                    "Eres un clasificador. Analiza el siguiente mensaje y responde únicamente con 'sí' "
                    "si es un saludo inicial (como hola, buenas, qué tal, etc.) o 'no' si no lo es. "
                    "No expliques nada más.")},
                {"role": "user", "content": mensaje_usuario}
            ],
            temperature=0,
            max_tokens=3
        )
        decision = respuesta.choices[0].message.content.strip().lower()
        return decision == "sí"
    except Exception as e:
        print(f"[ERROR GPT - clasificación de saludo] {e}")
        return False  # Si hay error, no saludamos por precaución

def generar_respuesta(mensaje_usuario, numero, historial):
    print("[GPT] Generando respuesta personalizada...")

    saludo_detectado = es_saludo_gpt(mensaje_usuario)

    mensaje_system = (
        "Eres Chatbot Ads Manager, un asistente inteligente que ayuda a personas sin experiencia a usar Google Ads. "
        "Estás conversando por WhatsApp con un usuario que ya interactuó contigo, así que debes sonar como alguien que ya está en conversación activa.\n\n"
    )

    if saludo_detectado:
        mensaje_system += "- El usuario acaba de saludarte. Puedes responder con un saludo cálido.\n"
    else:
        mensaje_system += "- No debes saludar. Responde directamente al contenido del mensaje.\n"

    mensaje_system += (
        "- Nunca vuelvas a presentarte como asistente o explicar tu propósito, a menos que el usuario lo pida explícitamente.\n"
        "- No repitas 'estoy aquí para ayudarte', 'soy un chatbot', ni similares.\n"
        "- Tus respuestas deben ser cálidas, útiles, breves y humanas.\n"
        "- Responde en un solo bloque de texto, de máximo 150 palabras y 6 líneas de WhatsApp.\n"
        "- Si puedes, usa listas o ejemplos cortos para explicar algo.\n"
        "- Usa emojis solo si refuerzan una actitud amigable o un cierre positivo. No uses más de uno por respuesta.\n"
        "- Nunca uses más de una exclamación consecutiva (evita '¡¡Hola!!').\n"
        "- Siempre responde en el idioma del usuario, con lenguaje natural y cercano.\n"
    )

    mensajes = [{"role": "system", "content": mensaje_system}]

    historial_filtrado = [
        mensaje for mensaje in historial
        if isinstance(mensaje, dict)
        and "role" in mensaje
        and "content" in mensaje
    ]
    mensajes.extend(historial_filtrado)

    try:
        response = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=500
        )

        respuesta = response.choices[0].message.content.strip()
        print("[GPT] Respuesta generada exitosamente.")
        return respuesta

    except Exception as e:
        print(f"[ERROR GPT] No se pudo generar la respuesta: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. ¿Podés intentar de nuevo?"



















from src.config import openai_client, GPT_MODEL, TEMPERATURA_CONVERSACION

def generar_respuesta(mensaje_usuario, numero, historial):
    print("[GPT] Generando respuesta personalizada...")

    # Prompt del sistema para conversación natural y enfocada en publicidad digital
    mensajes = [
        {"role": "system", "content": (
            "Eres Chatbot Ads Manager, un asistente inteligente que ayuda a personas sin experiencia a usar Google Ads. "
            "Estás conversando por WhatsApp con un usuario que ya interactuó contigo, así que debes sonar como alguien que ya está en conversación activa.\n\n"

            "INSTRUCCIONES ESTRICTAS:\n"
            "- Solo debes saludar (ej. 'hola', 'buenas') si el último mensaje del usuario es un saludo claro.\n"
            "- Nunca vuelvas a presentarte como asistente o explicar tu propósito, a menos que el usuario lo pida explícitamente.\n"
            "- No repitas 'estoy aquí para ayudarte', 'soy un chatbot', ni similares.\n"
            "- Tus respuestas deben ser cálidas, útiles, breves y humanas.\n"
            "- Responde en un solo bloque de texto, de máximo 150 palabras y 6 líneas de WhatsApp.\n"
            "- Si puedes, usa listas o ejemplos cortos para explicar algo.\n"
            "- Usa emojis solo si refuerzan una actitud amigable o un cierre positivo. No uses más de uno por respuesta.\n"
            "- Nunca uses más de una exclamación consecutiva (evita '¡¡Hola!!').\n"
            "- Siempre responde en el idioma del usuario, con lenguaje natural y cercano.\n\n"

            "Tu único objetivo es que el usuario comprenda cómo usar Google Ads de forma simple y se sienta cómodo conversando contigo."
        )}
    ]


    # Filtrar historial para evitar errores por mensajes mal formateados
    historial_filtrado = [
        mensaje for mensaje in historial
        if isinstance(mensaje, dict)
        and "role" in mensaje
        and "content" in mensaje
    ]
    mensajes.extend(historial_filtrado)

    try:
        response = openai_client.chat.completions.create(
            model=GPT_MODEL,  # GPT-3.5-Turbo
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,  # Recomendado: 0.7
            max_tokens=500
        )

        respuesta = response.choices[0].message.content.strip()
        print("[GPT] Respuesta generada exitosamente.")
        return respuesta

    except Exception as e:
        print(f"[ERROR GPT] No se pudo generar la respuesta: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. ¿Podés intentar de nuevo?"









CON ERROR DETECTADO EN ROLE


from src.config import openai_client, GPT_MODEL, TEMPERATURA_CONVERSACION

def generar_respuesta(mensaje_usuario, numero, historial):
    print("[GPT] Generando respuesta personalizada...")

    # Prompt del sistema para conversación natural y enfocada en publicidad digital
    mensajes = [
        {"role": "system", "content": (
            "Eres Chatbot Ads Manager, un asistente especializado en ayudar a personas sin experiencia a usar Google Ads. "
            "Respondes como si estuvieras en una charla por WhatsApp: con calidez, claridad y respuestas breves.\n\n"

            "INSTRUCCIONES:\n"
            "- Estrictamente solo puedes saludar si el usuario inicia la conversación con un saludo (como 'hola', 'buenas', etc.). En cualquier otro caso, no debes saludar.\n"
            "- No digas frases como 'soy un asistente' o 'fui creado para ayudarte'. Solo responde si el usuario pregunta quién eres.\n"
            "- Da respuestas claras y directas. Evita explicaciones largas o técnicas.\n"
            "- Tu respuesta estricatamente debe ser menor a 150 palabras.\n"
            "- Escribe en párrafos breves y fáciles de leer. No más de 6 líneas visuales en WhatsApp por respuesta.\n"
            "- Si puedes, usa listas o ejemplos sencillos.\n"
            "- Usa emojis solo si ayudan a la cercanía. No los repitas demasiado.\n"
            "- Responde siempre en el idioma del usuario.\n\n"

            "Tu objetivo es que el usuario entienda cómo usar Google Ads de forma simple y se sienta cómodo conversando contigo."
        )}
    ]



    # Agregar historial ya procesado (con inyecciones si corresponde)
    mensajes.extend(historial)

    try:
        response = openai_client.chat.completions.create(
            model=GPT_MODEL,  # GPT-3.5-Turbo
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,  # Recomendado: 0.7
            max_tokens=500
        )

        respuesta = response.choices[0].message.content.strip()
        print("[GPT] Respuesta generada exitosamente.")
        return respuesta

    except Exception as e:
        print(f"[ERROR GPT] No se pudo generar la respuesta: {e}")
        return "Lo siento, hubo un problema al generar la respuesta. ¿Podés intentar de nuevo?"


'''