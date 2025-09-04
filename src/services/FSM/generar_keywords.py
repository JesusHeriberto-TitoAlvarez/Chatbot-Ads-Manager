from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_generacion_keywords(numero_usuario, mensaje_usuario):
    """
    Procesa la respuesta del usuario para generar 3 palabras clave de máximo 25 caracteres.
    Si no se detectan bien, vuelve a pedir amablemente más información.
    """

    # Paso 1: Generar las palabras clave con base en la descripción del negocio del usuario
    try:
        prompt = [
            {"role": "system", "content": (
                "Eres un chatbot profesional conectado con Google Ads especializado en generar palabras clave precisas y relevantes para campañas publicitarias.\n"
                "El usuario te proporcionará una breve descripción de su negocio y su objetivo principal.\n\n"
                "**Tu tarea es OBLIGATORIAMENTE:**\n"
                "- Generar exactamente **3 palabras clave** basadas en la información dada.\n"
                "- Cada palabra o frase clave debe tener como máximo **25 caracteres**.\n"
                "- Si el contenido del usuario es muy extenso, debes **resumir o parafrasear creativamente** sin inventar información nueva.\n"
                "- Separa las palabras clave usando el símbolo `|` (barra vertical) **sin espacios extra**.\n"
                "- No expliques, no agregues comentarios, no completes con ejemplos adicionales, no inventes temas nuevos.\n"
                "- Solo responde las 3 palabras clave, unidas por `|`.\n\n"
                "**IMPORTANTE:**\n"
                "- Si no puedes identificar claramente 3 palabras clave válidas respetando las reglas anteriores, debes devolver exactamente la palabra: `NO_KEYWORDS`.\n"
                "- No improvises si no puedes cumplir las reglas.\n\n"
                "**Ejemplo de entrada:** 'Vendo colchones ortopédicos y quiero destacar la calidad y los descuentos.'\n"
                "**Ejemplo de salida correcta:** 'colchones baratos|descuento directo|almohadas confort'"
            )},
            {"role": "user", "content": mensaje_usuario}
        ]


        # Solicitar la respuesta al modelo GPT
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=100
        )

        keywords_crudas = respuesta.choices[0].message.content.strip()

    except Exception:
        # Error de conexión o fallo general
        return "Hubo un problema al generar tus palabras clave. ¿Podrías describirme nuevamente tu negocio y objetivo, por favor?"

    # Paso 2: Validar el formato de la respuesta
    if keywords_crudas.count("|") != 2:
        keywords_limpias = "NO_KEYWORDS"
    else:
        keywords_list = [k.strip() for k in keywords_crudas.split("|") if k.strip()]
        if any(len(k) > 25 for k in keywords_list):
            keywords_limpias = "NO_KEYWORDS"
        else:
            keywords_limpias = keywords_crudas

    # Paso 3: Si no son válidas, generar respuesta cálida y natural para reintentar
    if keywords_limpias == "NO_KEYWORDS":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

        prompt_reintento = [{
            "role": "system",
            "content": (
                f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios.\n"
                f"Le pediste que describiera los productos o servicios que ofrece y a qué tipo de personas quiere llegar, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                f"Este es el historial reciente de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'¿Qué productos o servicios vendes y qué tipo de personas quieres que encuentren tu anuncio? "
                "Y si deseas salir del proceso, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                "No repitas literal lo que dijo el usuario. No menciones que estás leyendo historial. Usa máximo 5 líneas, manteniendo un tono humano, útil y de acompañamiento."
            )
        }]

        prompt_reintento.extend(historial)

        # Generar la respuesta cálida
        respuesta_reintento = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt_reintento,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        mensaje_reintento = respuesta_reintento.choices[0].message.content.strip()
        guardar_mensaje(numero_usuario, "assistant", mensaje_reintento)
        return mensaje_reintento

    # Paso 4: Guardar las keywords válidas y continuar con el flujo del anuncio
    update_user_field(numero_usuario, "Keywords", keywords_limpias)
    update_user_field(numero_usuario, "Estado Anuncio", "Keywords Generadas")

    print(f"[LOG] Palabras clave generadas correctamente: {keywords_limpias} para número: {numero_usuario}")

    # Continuar con el flujo del anuncio una vez registradas las keywords
    from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
    return ejecutar_flujo_creacion_campana(numero_usuario)
