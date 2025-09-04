from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_costo_google_ads(numero_usuario):
    """
    Genera una respuesta natural y contextualizada para explicar cuánto cuesta Google Ads,
    mostrando que se puede empezar con montos bajos y evaluar resultados antes de continuar.
    """

    historial_completo = leer_historial(numero_usuario)

    # Separar mensajes por rol
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    # Fusionar y ordenar cronológicamente
    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    # DEBUG: mostrar historial usado para esta intención
    print("[DEBUG - HISTORIAL COSTO_GOOGLE_ADS] Mensajes recientes para el prompt:")
    for i, h in enumerate(historial_reciente):
        print(f"[{i}] ({h['role']}) → {h['content']}")

    mensajes = [
        {"role": "system", "content": (
            "El usuario acaba de preguntar cuánto cuesta usar Google Ads. Tu tarea es responder de forma clara, "
            "accesible y tranquilizadora. Debes explicar que no hay un precio fijo, y que se puede empezar con montos bajos "
            "como 5 Bs por día o incluso menos, hacer una prueba por una semana y luego decidir si continuar o detenerlo. \n\n"

            "INSTRUCCIONES:\n"
            "- No digas saludos ni repitas la pregunta.\n"
            "- Menciona que cada persona elige su presupuesto.\n"
            "- Usa ejemplos como: gastar Bs 5 al día, gastar Bs 35 en una semana, o invertir solo Bs 100 al mes.\n"
            "- Aclara que si no le convence, puede detener la campaña cuando quiera.\n"
            "- Escribe como en un chat: directo, cálido, frases cortas.\n"
            "- Puedes usar un emoji, pero solo uno.\n"
            "- No más de 6 líneas visibles en WhatsApp."
        )}
    ]

    mensajes.extend(historial_reciente)

    try:
        print("[GPT] Generando respuesta para intención 'costo Google Ads'...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=220
        )
        print("[GPT] Respuesta generada exitosamente para intención 'costo Google Ads'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_costo_google_ads] {e}")
        return (
            "Google Ads no tiene un costo fijo. Tú decides cuánto invertir según tu bolsillo. "
            "Por ejemplo, puedes empezar con solo Bs 5 al día (Bs 35 a la semana), ver los resultados, y luego decidir. "
            "Si no te convence, puedes pausar o cambiar el anuncio en cualquier momento. 😊"
        )











'''
from src.config import openai_client, GPT_MODEL_GENERAL, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_costo_google_ads(numero_usuario):
    """
    Genera una respuesta natural y contextualizada para explicar cuánto cuesta Google Ads,
    mostrando que se puede empezar con montos bajos y evaluar resultados antes de continuar.
    """

    historial_completo = leer_historial(numero_usuario)

    # Separar mensajes por rol
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    # Fusionar y ordenar cronológicamente
    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    mensajes = [
        {"role": "system", "content": (
            "El usuario acaba de preguntar cuánto cuesta usar Google Ads. Tu tarea es responder de forma clara, "
            "accesible y tranquilizadora. Debes explicar que no hay un precio fijo, y que se puede empezar con montos bajos "
            "como 5 Bs por día o incluso menos, hacer una prueba por una semana y luego decidir si continuar o detenerlo. \n\n"

            "INSTRUCCIONES:\n"
            "- No digas saludos ni repitas la pregunta.\n"
            "- Menciona que cada persona elige su presupuesto.\n"
            "- Usa ejemplos como: gastar Bs 5 al día, gastar Bs 35 en una semana, o invertir solo Bs 100 al mes.\n"
            "- Aclara que si no le convence, puede detener la campaña cuando quiera.\n"
            "- Escribe como en un chat: directo, cálido, frases cortas.\n"
            "- Puedes usar un emoji, pero solo uno.\n"
            "- No más de 6 líneas visibles en WhatsApp."
        )}
    ]

    mensajes.extend(historial_reciente)

    try:
        print("[GPT] Generando respuesta para intención 'costo Google Ads'...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_GENERAL,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=220
        )
        print("[GPT] Respuesta generada exitosamente para intención 'costo Google Ads'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_costo_google_ads] {e}")
        return (
            "Google Ads no tiene un costo fijo. Tú decides cuánto invertir según tu bolsillo. "
            "Por ejemplo, puedes empezar con solo Bs 5 al día (Bs 35 a la semana), ver los resultados, y luego decidir. "
            "Si no te convence, puedes pausar o cambiar el anuncio en cualquier momento. 😊"
        )
'''
