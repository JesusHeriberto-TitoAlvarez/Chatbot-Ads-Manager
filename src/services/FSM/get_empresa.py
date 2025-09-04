from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_nombre_empresa(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del mensaje usando GPT y lo guarda en Google Sheets.
    Si es válido, actualiza el estado y vuelve a ejecutar el flujo principal.
    Si es inválido, explica con naturalidad y espera una nueva entrada.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear campañas publicitarias.\n"
            "Tu tarea específica es extraer únicamente el **NOMBRE REAL DEL NEGOCIO**, empresa o emprendimiento, a partir de mensajes informales de WhatsApp.\n"
            "Ejemplo: si el mensaje dice 'mi negocio se llama Zapatería Tito', debes devolver solo: 'Zapatería Tito'.\n"
            "No devuelvas frases genéricas como 'mi negocio', 'mi empresa', 'una tienda', 'un emprendimiento'.\n"
            "No completes, no inventes, no agregues descripciones o ubicaciones. No incluyas saludos ni explicaciones.\n"
            "Devuelve solo el nombre limpio y directo del negocio, tal como se usaría en una campaña de Google Ads. Sin comillas ni puntuación.\n"
            "El resultado debe ser una frase corta y capitalizada correctamente, usable en un anuncio formal.\n\n"
            "**IMPORTANTE:** Si no puedes detectar un nombre válido de empresa, debes devolver exactamente la palabra: `NO_EMPRESA`.\n"
            "No expliques, no razones, no devuelvas ningún otro texto. Solo devuelve `NO_EMPRESA` si no encuentras un nombre útil y real."
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

        empresa_cruda = respuesta.choices[0].message.content.strip()
        
        if empresa_cruda.strip().upper() == "NO_EMPRESA":
            empresa_limpia = "NO_EMPRESA"
        else:
            empresa_limpia = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9 ]", "", empresa_cruda).strip().title()


        if empresa_limpia.upper() == "NO_EMPRESA" or len(empresa_limpia) < 2:

            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear sus anuncios.\n"
                    f"Le pediste que te diga cómo se llama su empresa o emprendimiento, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
                    "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
                    "'Para poder avanzar con la creación de tus anuncios, necesito saber cómo se llama tu empresa o emprendimiento. "
                    "Pero si deseas desconectarte de Google Ads, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                    "Usa máximo 5 líneas. No repitas lo que dijo el usuario literalmente. No digas que estás leyendo el historial. Mantén el tono humano y útil."
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

        # ✅ Empresa válida
        update_user_field(numero_usuario, "Campaign Name", empresa_limpia)
        update_user_field(numero_usuario, "Estado Campana", "Empresa Registrada")

        print(f"[LOG] Empresa registrada correctamente: {empresa_limpia} para número: {numero_usuario}")

        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar el nombre de tu empresa. ¿Podrías repetir el nombre de tu empresa por favor?"






'''
from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_nombre_empresa(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del mensaje usando GPT y lo guarda en Google Sheets.
    Si es válido, actualiza el estado y vuelve a ejecutar el flujo principal.
    Si es inválido, explica con naturalidad y espera una nueva entrada.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear campañas publicitarias.\n"
            "Tu tarea específica es extraer únicamente el **NOMBRE REAL DEL NEGOCIO**, empresa o emprendimiento, a partir de mensajes informales de WhatsApp.\n"
            "Ejemplo: si el mensaje dice 'mi negocio se llama Zapatería Tito', debes devolver solo: 'Zapatería Tito'.\n"
            "No devuelvas frases genéricas como 'mi negocio', 'mi empresa', 'una tienda', 'un emprendimiento'.\n"
            "No completes, no inventes, no agregues descripciones o ubicaciones. No incluyas saludos ni explicaciones.\n"
            "Devuelve solo el nombre limpio y directo del negocio, tal como se usaría en una campaña de Google Ads. Sin comillas ni puntuación.\n"
            "El resultado debe ser una frase corta y capitalizada correctamente, usable en un anuncio formal.\n\n"
            "**IMPORTANTE:** Si no puedes detectar un nombre válido de empresa, debes devolver exactamente la palabra: `NO_EMPRESA`.\n"
            "No expliques, no razones, no devuelvas ningún otro texto. Solo devuelve `NO_EMPRESA` si no encuentras un nombre útil y real."
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

        empresa_cruda = respuesta.choices[0].message.content.strip()
        
        if empresa_cruda.strip().upper() == "NO_EMPRESA":
            empresa_limpia = "NO_EMPRESA"
        else:
            empresa_limpia = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]", "", empresa_cruda.split()[0]).title()

        if empresa_limpia.upper() == "NO_EMPRESA" or len(empresa_limpia) < 2:

            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear sus anuncios.\n"
                    f"Le pediste que te diga cómo se llama su empresa o emprendimiento, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
                    "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
                    "'Para poder avanzar con la creación de tus anuncios, necesito saber cómo se llama tu empresa o emprendimiento. "
                    "Pero si deseas desconectarte de Google Ads, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                    "Usa máximo 5 líneas. No repitas lo que dijo el usuario literalmente. No digas que estás leyendo el historial. Mantén el tono humano y útil."
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

        # ✅ Empresa válida
        update_user_field(numero_usuario, "Campaign Name", empresa_limpia)
        update_user_field(numero_usuario, "Estado Campana", "Empresa Registrada")

        print(f"[LOG] Empresa registrada correctamente: {empresa_limpia} para número: {numero_usuario}")

        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar el nombre de tu empresa. ¿Podrías repetir el nombre de tu empresa por favor?"














from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_nombre_empresa(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del negocio desde el mensaje del usuario usando GPT.
    Si es válido, lo guarda en Google Sheets y continúa el flujo.
    Si no es válido, solicita nuevamente el nombre del negocio de forma cálida y contextual.
    """
    
    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear campañas publicitarias.\n"
            "Tu tarea específica es extraer únicamente el **NOMBRE REAL DEL NEGOCIO**, empresa o emprendimiento, a partir de mensajes informales de WhatsApp.\n"
            "Ejemplo: si el mensaje dice 'mi negocio se llama Zapatería Tito', debes devolver solo: 'Zapatería Tito'.\n"
            "No devuelvas frases genéricas como 'mi negocio', 'mi empresa', 'una tienda', 'un emprendimiento'.\n"
            "No completes, no inventes, no agregues descripciones o ubicaciones. No incluyas saludos ni explicaciones.\n"
            "Devuelve solo el nombre limpio y directo del negocio, tal como se usaría en una campaña de Google Ads. Sin comillas ni puntuación.\n"
            "El resultado debe ser una frase corta y capitalizada correctamente, usable en un anuncio formal.\n\n"
            "**IMPORTANTE:** Si no puedes detectar un nombre válido de empresa, debes devolver exactamente la palabra: `NO_EMPRESA`.\n"
            "No expliques, no razones, no devuelvas ningún otro texto. Solo devuelve `NO_EMPRESA` si no encuentras un nombre útil y real."
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

        empresa_cruda = respuesta.choices[0].message.content.strip()

        if empresa_cruda.strip().upper() == "NO_EMPRESA" or len(empresa_cruda) < 2:
            return volver_a_pedir_nombre_empresa(numero_usuario, mensaje_usuario)

        empresa_limpia = re.sub(r"[\"'´`<>]", "", empresa_cruda).strip().title()

        update_user_field(numero_usuario, "Campaign Name", empresa_limpia)
        update_user_field(numero_usuario, "Estado Campana", "Empresa Registrada")

        print(f"[LOG] Empresa registrada correctamente: {empresa_limpia} para número: {numero_usuario}")

        # ✅ Importación diferida para evitar circular import
        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar el nombre de tu empresa. ¿Podrías repetirlo por favor?"


def volver_a_pedir_nombre_empresa(numero_usuario, mensaje_usuario):
    """
    Si no se puede extraer el nombre del negocio, se genera una respuesta cálida que
    parafrasea la idea de forma natural y conecta con el historial reciente.
    """

    historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
    historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

    prompt_reintento = [{
        "role": "system",
        "content": (
            f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear sus anuncios.\n"
            f"Le pediste que te diga cómo se llama su empresa o emprendimiento, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
            f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
            f"{historial_texto}\n"
            "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
            "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
            "'Para poder avanzar con la creación de tus anuncios, necesito saber cómo se llama tu empresa o emprendimiento. "
            "Pero si deseas desconectarte de Google Ads, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
            "Usa máximo 5 líneas. No repitas lo que dijo el usuario literalmente. No digas que estás leyendo el historial. Mantén el tono humano y útil."
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
import re

def procesar_nombre_empresa(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del negocio desde el mensaje del usuario usando GPT.
    Si es válido, lo guarda en Google Sheets y continúa el flujo.
    Si no es válido, solicita nuevamente el nombre del negocio de forma cálida y contextual.
    """
    
    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear campañas publicitarias.\n"
            "Tu tarea específica es extraer únicamente el **NOMBRE REAL DEL NEGOCIO**, empresa o emprendimiento, a partir de mensajes informales de WhatsApp.\n"
            "Ejemplo: si el mensaje dice 'mi negocio se llama Zapatería Tito', debes devolver solo: 'Zapatería Tito'.\n"
            "No devuelvas frases genéricas como 'mi negocio', 'mi empresa', 'una tienda', 'un emprendimiento'.\n"
            "No completes, no inventes, no agregues descripciones o ubicaciones. No incluyas saludos ni explicaciones.\n"
            "Devuelve solo el nombre limpio y directo del negocio, tal como se usaría en una campaña de Google Ads. Sin comillas ni puntuación.\n"
            "El resultado debe ser una frase corta y capitalizada correctamente, usable en un anuncio formal.\n\n"
            "**IMPORTANTE:** Si no puedes detectar un nombre válido de empresa, debes devolver exactamente la palabra: `NO_EMPRESA`.\n"
            "No expliques, no razones, no devuelvas ningún otro texto. Solo devuelve `NO_EMPRESA` si no encuentras un nombre útil y real."
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

        empresa_cruda = respuesta.choices[0].message.content.strip()

        if empresa_cruda.strip().upper() == "NO_EMPRESA" or len(empresa_cruda) < 2:
            return volver_a_pedir_nombre_empresa(numero_usuario, mensaje_usuario)

        empresa_limpia = re.sub(r"[\"'´`<>]", "", empresa_cruda).strip().title()

        update_user_field(numero_usuario, "Business Name", empresa_limpia)
        update_user_field(numero_usuario, "Estado Campana", "Empresa Registrada")

        print(f"[LOG] Empresa registrada correctamente: {empresa_limpia} para número: {numero_usuario}")

        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar el nombre de tu empresa. ¿Podrías repetirlo por favor?"



def volver_a_pedir_nombre_empresa(numero_usuario, mensaje_usuario):
    """
    Si no se puede extraer el nombre del negocio, se genera una respuesta cálida que
    parafrasea la idea de forma natural y conecta con el historial reciente.
    """

    historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
    historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

    prompt_reintento = [{
        "role": "system",
        "content": (
            f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear sus anuncios.\n"
            f"Le pediste que te diga cómo se llama su empresa o emprendimiento, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
            f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
            f"{historial_texto}\n"
            "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
            "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
            "'Para poder avanzar con la creación de tus anuncios, necesito saber cómo se llama tu empresa o emprendimiento. "
            "Pero si deseas desconectarte de Google Ads, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
            "Usa máximo 5 líneas. No repitas lo que dijo el usuario literalmente. No digas que estás leyendo el historial. Mantén el tono humano y útil."
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