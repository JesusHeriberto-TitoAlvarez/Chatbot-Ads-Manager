from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_generacion_descripciones(numero_usuario, mensaje_usuario):
    """
    Procesa la respuesta del usuario para generar 3 descripciones publicitarias de máximo 90 caracteres.
    Si no se detectan bien, vuelve a pedir amablemente más información.
    """

    # Paso 1: Intentar generar las descripciones
    try:
        prompt = [
            {"role": "system", "content": (
                "Eres un chatbot profesional conectado con Google Ads especializado en crear descripciones publicitarias claras, breves y atractivas para campañas en línea.\n"
                "El usuario te proporcionará una breve descripción de su negocio y su objetivo principal.\n\n"
                "**Tu tarea es OBLIGATORIAMENTE:**\n"
                "- Generar exactamente **3 descripciones** basadas en la información dada.\n"
                "- Cada descripción debe tener como máximo **90 caracteres**.\n"
                "- Si el contenido del usuario es muy extenso, debes **resumir o parafrasear creativamente** sin inventar información nueva.\n"
                "- Separa las descripciones usando el símbolo `|` (barra vertical) **sin espacios extra**.\n"
                "- No expliques, no agregues comentarios, no completes con ejemplos adicionales, no inventes temas nuevos.\n"
                "- Solo responde las 3 descripciones, unidas por `|`.\n\n"
                "**IMPORTANTE:**\n"
                "- Si no puedes identificar claramente 3 descripciones válidas respetando las reglas anteriores, debes devolver exactamente la palabra: `NO_DESCRIPCIONES`.\n"
                "- No improvises si no puedes cumplir las reglas.\n\n"
                "**Ejemplo de entrada:** 'Tengo una tienda de ropa y quiero aumentar mis ventas online.'\n"
                "**Ejemplo de salida correcta:** 'Ropa a la moda|Compra segura online|Descuentos semanales'"
            )},
            {"role": "user", "content": mensaje_usuario}
        ]

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=150
        )

        descripciones_crudas = respuesta.choices[0].message.content.strip()

    except Exception:
        return "Hubo un problema al generar tus descripciones. ¿Podrías describirme nuevamente tu negocio y objetivo, por favor?"

    # Paso 2: Procesar descripciones fuera del try
    if descripciones_crudas.count("|") != 2:
        descripciones_limpias = "NO_DESCRIPCIONES"
    else:
        descripciones_list = [d.strip() for d in descripciones_crudas.split("|") if d.strip()]
        if any(len(d) > 90 for d in descripciones_list):
            descripciones_limpias = "NO_DESCRIPCIONES"
        else:
            descripciones_limpias = descripciones_crudas

    if descripciones_limpias == "NO_DESCRIPCIONES":
        # No se detectaron bien las descripciones
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

        prompt_reintento = [{
            "role": "system",
            "content": (
                f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios.\n"
                f"Le pediste que describiera su producto o servicio más importante y qué lo hace especial, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                f"Este es el historial reciente de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Para ayudarte a crear buenas descripciones, necesito que me cuentes cuál es tu producto o servicio más importante, "
                "y qué beneficio lo hace especial o diferente frente a otros negocios. "
                "Si deseas salir del proceso, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                "No repitas literal lo que dijo el usuario. No menciones que estás leyendo historial. Usa máximo 5 líneas, con un tono cercano, cálido y profesional."
            )
        }]

        prompt_reintento.extend(historial)

        respuesta_reintento = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt_reintento,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        mensaje_reintento = respuesta_reintento.choices[0].message.content.strip()
        guardar_mensaje(numero_usuario, "assistant", mensaje_reintento)
        return mensaje_reintento

    # ✅ Descripciones válidas
    update_user_field(numero_usuario, "Descriptions", descripciones_limpias)
    update_user_field(numero_usuario, "Estado Anuncio", "Descripciones Generadas")

    print(f"[LOG] Descripciones generadas correctamente: {descripciones_limpias} para número: {numero_usuario}")

    # Importar dinámicamente para evitar importación circular
    from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
    return ejecutar_flujo_creacion_campana(numero_usuario)
