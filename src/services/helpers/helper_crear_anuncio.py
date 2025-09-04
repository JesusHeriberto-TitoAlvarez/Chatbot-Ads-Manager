# src/services/helpers/helper_crear_anuncio.py

from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_CONVERSACION
from src.data.firestore_storage import leer_historial
from src.data.chatbot_sheet_connector import get_user_field

def iniciar_flujo_creacion_anuncio(numero_usuario):
    """
    Genera una respuesta contextualizada para iniciar el proceso de creación de campaña o anuncio,
    según el estado de la columna 'Estado Campana' del usuario en Google Sheets.
    """

    try:
        estado_campana = get_user_field(numero_usuario, "Estado Campana")
        print(f"[HELPER CREAR ANUNCIO] Estado Campana detectado para {numero_usuario}: {estado_campana}")

        # Leer historial reciente
        historial_completo = leer_historial(numero_usuario)
        ultimos_usuario = [m for m in historial_completo if m["role"] == "user"][-6:]
        ultimos_bot = [m for m in historial_completo if m["role"] == "assistant"][-6:]
        historial_ordenado = sorted(ultimos_usuario + ultimos_bot, key=lambda x: x.get("timestamp", ""))

        # Crear prompt base según estado
        if estado_campana != "Campana Complete":
            print("[HELPER CREAR CAMPAÑA] Generando prompt para INICIAR CAMPAÑA.")
            mensaje_sistema = (
                "Eres un chatbot conectado directamente con Google Ads que ayuda a personas sin experiencia a crear anuncios desde cero.\n"
                "Lee el contexto del chat reciente y responde de forma cálida, clara y natural. PARAFRASEA este mensaje dentro de la conversación:\n\n"
                "Puedo encargarme de crear y publicar tus anuncios en Google Ads usando una conexión directa con la plataforma."
                "Para comenzar, es necesario crear una campaña, ya que es el primer paso obligatorio que exige Google. "
                "No te preocupes, este proceso es totalmente gratuito y te permitirá probar cómo funciona la publicidad online. "
                "Si estás listo para dar el primer paso, solo escribe *CREAR CAMPAÑA* (todo en mayúsculas y sin signos).'\n\n"
                "No repitas el texto exacto. Integra el mensaje de forma natural según lo que el usuario pregunte, usando como máximo 6 líneas de WhatsApp."
            )


        else:
            print("[HELPER CREAR ANUNCIO] Generando prompt para INICIAR ANUNCIOS.")
            mensaje_sistema = (
                "Eres un chatbot que ayuda a crear anuncios en Google Ads.\n"
                "Analiza el contexto del chat reciente y responde de forma cálida y natural, integrando este mensaje dentro del flujo:\n\n"
                "'Me alegra que ya hayas creado la campaña para tu negocio o empresa, ahora sí podemos crear tus anuncios. "
                "Si así lo deseas solo dime *Crear anuncios* por favor.'\n\n"
                "No repitas ese texto exacto. Combínalo naturalmente con lo anterior. Usa máximo 6 líneas de WhatsApp."
            )

        mensajes = [{"role": "system", "content": mensaje_sistema}]
        mensajes.extend(historial_ordenado)

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=250
        )

        respuesta_final = respuesta.choices[0].message.content.strip()
        print(f"[HELPER CREAR ANUNCIO] Respuesta generada correctamente para {numero_usuario}.")
        return respuesta_final

    except Exception as e:
        print(f"[ERROR HELPER CREAR ANUNCIO] {e}")
        return (
            "Estoy listo para ayudarte con tu campaña en Google Ads. Si quieres empezar, solo dime *Crear campaña* o *Crear anuncios*, según corresponda. 😉"
        )
