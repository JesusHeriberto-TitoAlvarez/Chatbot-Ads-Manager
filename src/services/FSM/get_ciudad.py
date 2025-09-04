from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_ciudad_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae la ciudad del mensaje usando GPT y la guarda en Google Sheets.
    Si es válida, actualiza el estado y vuelve a ejecutar el flujo principal.
    Si es inválida, explica con naturalidad y espera una nueva entrada.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads que está ayudando a personas a crear campañas publicitarias.\n"
            "Tu tarea es extraer únicamente el **nombre de la ciudad o departamento** donde el usuario desea mostrar su anuncio.\n\n"
            "Ejemplo: si el mensaje dice 'quiero publicitar en La Paz', debes devolver únicamente: 'La Paz'.\n"
            "No devuelvas frases genéricas como 'mi ciudad', 'cualquier lugar', 'todo Bolivia', ni explicaciones.\n"
            "Devuelve solo el nombre propio de la ciudad o región, sin adornos ni puntuación adicional.\n\n"
            "**IMPORTANTE:** Si no puedes identificar una ciudad válida, debes devolver exactamente la palabra: `NO_CIUDAD`.\n"
            "No expliques, no razones, no completes. Solo devuelve `NO_CIUDAD` si no puedes extraer un destino válido."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=20
        )

        ciudad_cruda = respuesta.choices[0].message.content.strip()
        
        if ciudad_cruda.strip().upper() == "NO_CIUDAD":
            ciudad_limpia = "NO_CIUDAD"
        else:
            ciudad_limpia = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]", "", ciudad_cruda.strip()).title()

        if ciudad_limpia.upper() == "NO_CIUDAD" or len(ciudad_limpia) < 2:

            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está guiando a un usuario por WhatsApp para crear una campaña publicitaria.\n"
                    f"Le pediste que indique la ciudad o departamento donde desea mostrar su anuncio, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"Este es el historial reciente de su conversación:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes responder de forma cálida, amigable y natural, como si continuaras la charla por WhatsApp.\n\n"
                    "OBLIGATORIAMENTE debes PARAFRASEAR la siguiente idea dentro del mensaje:\n"
                    "'Para poder mostrar tu anuncio, necesito saber en qué ciudad o departamento de Bolivia deseas hacerlo. "
                    "Y si deseas salir del proceso, puedes escribir SALIR en mayúsculas.'\n\n"
                    "NO repitas literal lo que dijo el usuario. NO digas que estás leyendo el historial. Usa máximo 5 líneas, lenguaje humano, cálido y funcional."
                )
            }]
            prompt_reintento.extend(historial)

            respuesta_reintento = openai_client.chat.completions.create(
                model=GPT_MODEL_AVANZADO,
                messages=prompt_reintento,
                temperature=TEMPERATURA_CONVERSACION,
                max_tokens=200
            )

            mensaje_reintento = respuesta_reintento.choices[0].message.content.strip()
            guardar_mensaje(numero_usuario, "assistant", mensaje_reintento)
            return mensaje_reintento

        # ✅ Ciudad válida
        update_user_field(numero_usuario, "Segmentation", ciudad_limpia)
        update_user_field(numero_usuario, "Estado Campana", "Ciudad Registrada")

        print(f"[LOG] Ciudad registrada correctamente: {ciudad_limpia} para número: {numero_usuario}")

        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar la ciudad. ¿Podrías repetirla por favor?"





'''
from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_ciudad_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae la ciudad del mensaje del usuario y la guarda si es válida.
    Si no es válida, pide la ciudad nuevamente de forma natural y cálida.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads que está ayudando a personas a crear campañas publicitarias.\n"
            "Tu tarea es extraer únicamente el **nombre de la ciudad o departamento** donde el usuario desea mostrar su anuncio.\n\n"
            "Ejemplo: si el mensaje dice 'quiero publicitar en La Paz', debes devolver únicamente: 'La Paz'.\n"
            "No devuelvas frases genéricas como 'mi ciudad', 'cualquier lugar', 'todo Bolivia', ni explicaciones.\n"
            "Devuelve solo el nombre propio de la ciudad o región, sin adornos ni puntuación adicional.\n\n"
            "**IMPORTANTE:** Si no puedes identificar una ciudad válida, debes devolver exactamente la palabra: `NO_CIUDAD`.\n"
            "No expliques, no razones, no completes. Solo devuelve `NO_CIUDAD` si no puedes extraer un destino válido."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=20
        )

        ciudad_cruda = respuesta.choices[0].message.content.strip()

        if ciudad_cruda.strip().upper() == "NO_CIUDAD" or len(ciudad_cruda) < 2:
            return volver_a_pedir_ciudad(numero_usuario, mensaje_usuario)

        ciudad_limpia = re.sub(r"[\"'´`<>]", "", ciudad_cruda).strip().title()

        update_user_field(numero_usuario, "Segmentation", ciudad_limpia)
        update_user_field(numero_usuario, "Estado Campana", "Ciudad Registrada")

        print(f"[LOG] Ciudad registrada correctamente: {ciudad_limpia} para número: {numero_usuario}")

        # ✅ Importación diferida para evitar circular import
        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar la ciudad. ¿Podrías repetirla por favor?"


def volver_a_pedir_ciudad(numero_usuario, mensaje_usuario):
    """
    Genera un mensaje natural que explica al usuario que necesitamos conocer la ciudad
    para continuar, utilizando el historial real de la conversación.
    """

    historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
    historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

    prompt_reintento = [{
        "role": "system",
        "content": (
            f"Eres un chatbot profesional conectado con Google Ads que está guiando a un usuario por WhatsApp para crear una campaña publicitaria.\n"
            f"Le pediste que indique la ciudad o departamento donde desea mostrar su anuncio, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
            f"Este es el historial reciente de su conversación:\n\n"
            f"{historial_texto}\n"
            "Ahora debes responder de forma cálida, amigable y natural, como si continuaras la charla por WhatsApp.\n\n"
            "OBLIGATORIAMENTE debes PARAFRASEAR la siguiente idea dentro del mensaje:\n"
            "'Para poder mostrar tu anuncio, necesito saber en qué ciudad o departamento de Bolivia deseas hacerlo. "
            "Y si deseas salir del proceso, puedes escribir SALIR en mayúsculas.'\n\n"
            "NO repitas literal lo que dijo el usuario. NO digas que estás leyendo el historial. Usa máximo 5 líneas, lenguaje humano, cálido y funcional."
        )
    }]
    prompt_reintento.extend(historial)

    respuesta = openai_client.chat.completions.create(
        model=GPT_MODEL_PRECISO,
        messages=prompt_reintento,
        temperature=TEMPERATURA_CONVERSACION,
        max_tokens=200
    )

    mensaje = respuesta.choices[0].message.content.strip()
    guardar_mensaje(numero_usuario, "assistant", mensaje)
    return mensaje


















from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
import re

def procesar_ciudad_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae la ciudad desde el mensaje del usuario usando GPT.
    Si es válida, la guarda en Google Sheets y continúa el flujo.
    Si no es válida, solicita nuevamente la ciudad de forma cálida y contextual.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear anuncios.\n"
            "Tu tarea específica es extraer únicamente el **nombre de la ciudad o departamento** donde el usuario desea mostrar su anuncio.\n\n"
            "Ejemplo: si el mensaje dice 'quiero publicitar en La Paz', debes devolver únicamente: 'La Paz'.\n\n"
            "El resultado debe ser una sola frase limpia, capitalizada correctamente, sin signos, comillas ni símbolos raros.\n"
            "No devuelvas frases genéricas como 'mi ciudad', 'cualquier lugar', 'toda Bolivia', ni devoluciones vagas o con errores ortográficos.\n"
            "No completes ni expliques. No agregues nada adicional como 'donde vivo' o 'en cualquier sitio'. Solo devuelve el nombre claro y usable de una ciudad o región boliviana.\n\n"
            "**IMPORTANTE:** Si no puedes identificar un nombre válido de ciudad o departamento, debes devolver exactamente: `NO_CIUDAD`.\n"
            "No justifiques. No devuelvas ningún otro texto. Solo responde con `NO_CIUDAD` si no puedes extraer un lugar válido."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]


    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=30
        )

        ciudad_cruda = respuesta.choices[0].message.content.strip()

        if ciudad_cruda.strip().upper() == "NO_CIUDAD" or len(ciudad_cruda) < 2:
            return volver_a_pedir_ciudad_usuario(numero_usuario, mensaje_usuario)

        ciudad_limpia = re.sub(r"[\"'´`<>]", "", ciudad_cruda).strip().title()

        update_user_field(numero_usuario, "Segmentation", ciudad_limpia)
        update_user_field(numero_usuario, "Estado Campana", "Ciudad Registrada")

        print(f"[LOG] Ciudad registrada correctamente: {ciudad_limpia} para número: {numero_usuario}")
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar la ciudad. ¿Podrías decirla de nuevo, por favor?"


def volver_a_pedir_ciudad_usuario(numero_usuario, mensaje_usuario):
    """
    Si no se puede extraer la ciudad, se genera una respuesta cálida que
    parafrasea la idea de forma natural y conecta con el historial reciente.
    """

    historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
    historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

    prompt_reintento = [{
        "role": "system",
        "content": (
            f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear una campaña publicitaria.\n"
            f"Le pediste que te indique la ciudad o departamento donde desea mostrar su anuncio, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
            f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
            f"{historial_texto}\n"
            "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
            "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
            "'Para poder mostrar tu anuncio, necesito saber en qué ciudad o departamento de Bolivia deseas hacerlo. "
            "Pero si deseas desconectarte de Google Ads, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
            "Usa máximo 5 líneas. No repitas lo que dijo el usuario literalmente. No menciones que estás leyendo el historial. Mantén el tono humano, cálido y útil."
        )
    }]

    prompt_reintento.extend(historial)

    respuesta = openai_client.chat.completions.create(
        model=GPT_MODEL_PRECISO,
        messages=prompt_reintento,
        temperature=TEMPERATURA_CONVERSACION,
        max_tokens=200
    )

    mensaje = respuesta.choices[0].message.content.strip()
    guardar_mensaje(numero_usuario, "assistant", mensaje)
    return mensaje

'''