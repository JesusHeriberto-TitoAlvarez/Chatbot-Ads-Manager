from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial

def obtener_respuesta_proposito(numero_usuario):
    """
    Genera una respuesta dinámica y cálida para explicar el propósito del chatbot,
    usando el historial reciente del usuario para mayor naturalidad.
    """

    historial_completo = leer_historial(numero_usuario)

    # Separar mensajes por rol
    ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
    ultimos_chatbot = [m for m in historial_completo if m["role"] == "assistant"][-6:]

    # Fusionar y ordenar cronológicamente
    historial_reciente = sorted(ultimos_usuario + ultimos_chatbot, key=lambda x: x.get("timestamp", ""))

    # Crear el prompt ajustado basado en el propósito del proyecto
    mensajes = [
        {"role": "system", "content": (
            "El usuario quiere saber cuál es el propósito del chatbot, para qué sirve o cómo puede ayudarle.\n"
            "Tu tarea es explicarlo de forma cercana, sencilla y empática, como si estuvieras conversando por WhatsApp con una persona que nunca usó publicidad digital.\n\n"

            "INSTRUCCIONES:\n"
            "- Explica que el chatbot fue creado para ayudar a personas en Bolivia que tienen un negocio o empresa y no tienen experiencia ni acceso a tarjetas internacionales.\n"
            "- Menciona que este servicio es gratuito y puede guiar paso a paso a través de WhatsApp.\n"
            "- Recalca que está hecho para que se pueda preguntar sin miedo, como a un amigo que no se burla.\n"
            "- Usa frases naturales, cálidas, en estilo chat, sin tecnicismos.\n"
            "- Máximo 8 líneas visibles en WhatsApp.\n"
            "- Usa solo un emoji si realmente aporta, y no repitas la pregunta del usuario."
        )}
    ]

    mensajes.extend(historial_reciente)

    try:
        print("[GPT] Generando respuesta para intención 'propósito'...")
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=220
        )
        print("[GPT] Respuesta generada exitosamente para intención 'propósito'.")
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR GPT - helper_proposito] {e}")
        return (
            "Este chatbot fue creado para ayudarte a entender cómo funciona la publicidad en línea, aunque no tengas experiencia. "
            "Es gratuito y pensado para personas de Bolivia que tienen un negocio o emprendimiento. Te explico todo paso a paso por WhatsApp 😊"
        )
