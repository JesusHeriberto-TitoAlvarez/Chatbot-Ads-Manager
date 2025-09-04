from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_monto_inversion(numero_usuario, mensaje_usuario):
    """
    Extrae el monto de inversión desde el mensaje usando GPT y lo guarda en Google Sheets.
    Si es válido, actualiza el estado y vuelve a ejecutar el flujo principal.
    Si es inválido, explica con naturalidad y espera una nueva entrada.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear campañas publicitarias.\n"
            "Tu tarea específica es extraer únicamente el **MONTO DIARIO DE INVERSIÓN** que el usuario desea destinar a su campaña, expresado en bolivianos.\n"
            "El resultado debe ser **únicamente un número entero positivo**, sin símbolos, sin decimales, sin texto explicativo ni palabras como 'bolivianos' o 'Bs'.\n"
            "Ejemplo: si el mensaje dice 'quiero invertir 50 bolivianos al día', debes devolver únicamente: 50\n\n"
            "No devuelvas palabras como 'cincuenta', no devuelvas frases largas ni repitas la oración del usuario.\n"
            "No incluyas signos como Bs, $, puntos, comas, o espacios. Solo un número limpio y usable como monto en Google Ads.\n\n"
            "**IMPORTANTE:** Si no puedes detectar un monto válido (por ejemplo si el usuario no dijo ningún número claro), debes devolver exactamente la palabra: `NO_MONTO`.\n"
            "No expliques, no razones, no devuelvas ningún otro texto. Solo `NO_MONTO` si no se encuentra un monto claro y usable."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=10
        )

        monto_crudo = respuesta.choices[0].message.content.strip()

        if monto_crudo.strip().upper() == "NO_MONTO":
            monto_limpio = "NO_MONTO"
        else:
            monto_limpio = re.sub(r"[^\d]", "", monto_crudo).strip()

        if monto_limpio.upper() == "NO_MONTO" or not monto_limpio.isdigit() or int(monto_limpio) < 1:

            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios por WhatsApp.\n"
                    f"Le pediste que te indique el monto que podría invertir por día en su campaña, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
                    "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
                    "'Para poder avanzar con la creación de tus anuncios, necesito saber cuánto podrías invertir por día en tu campaña. "
                    "Este monto es solo simbólico, no se realizará ningún cobro. "
                    "Pero si deseas desconectarte de Google Ads, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                    "Usa máximo 5 líneas. No repitas lo que dijo el usuario literalmente. No digas que estás leyendo el historial. Mantén el tono humano, cercano y útil, como si estuvieras charlando con un amigo."
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

        # ✅ Monto válido
        update_user_field(numero_usuario, "Requested Budget", monto_limpio)
        update_user_field(numero_usuario, "Estado Campana", "Monto Registrado")

        print(f"[LOG] Monto registrado correctamente: {monto_limpio} Bs para número: {numero_usuario}")

        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar el monto. ¿Podrías repetirlo por favor?"






'''
from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_monto_inversion(numero_usuario, mensaje_usuario):
    """
    Extrae el monto de inversión desde el mensaje del usuario y lo guarda en Google Sheets.
    Si es válido, actualiza el estado y vuelve a ejecutar el flujo principal.
    Si es inválido, explica con naturalidad y espera una nueva entrada.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear campañas publicitarias.\n"
            "Tu tarea específica es extraer únicamente el **MONTO DIARIO DE INVERSIÓN** que el usuario desea destinar a su campaña, expresado en bolivianos.\n"
            "El resultado debe ser **únicamente un número entero positivo**, sin símbolos, sin decimales, sin texto explicativo ni palabras como 'bolivianos' o 'Bs'.\n"
            "Ejemplo: si el mensaje dice 'quiero invertir 50 bolivianos al día', debes devolver únicamente: 50\n\n"
            "No devuelvas palabras como 'cincuenta', no devuelvas frases largas ni repitas la oración del usuario.\n"
            "No incluyas signos como Bs, $, puntos, comas, o espacios. Solo un número limpio y usable como monto en Google Ads.\n\n"
            "**IMPORTANTE:** Si no puedes detectar un monto válido (por ejemplo si el usuario no dijo ningún número claro), debes devolver exactamente la palabra: `NO_MONTO`.\n"
            "No expliques, no razones, no devuelvas ningún otro texto. Solo `NO_MONTO` si no se encuentra un monto claro y usable."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=10
        )

        monto_crudo = respuesta.choices[0].message.content.strip()

        if monto_crudo.strip().upper() == "NO_MONTO":
            monto_limpio = "NO_MONTO"
        else:
            monto_limpio = re.sub(r"[^\d]", "", monto_crudo).strip()

        if monto_limpio.upper() == "NO_MONTO" or not monto_limpio.isdigit() or int(monto_limpio) < 1:
            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios por WhatsApp.\n"
                    f"Le pediste que te indique el monto que podría invertir por día en su campaña, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
                    "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
                    "'Para poder avanzar con la creación de tus anuncios, necesito saber cuánto podrías invertir por día en tu campaña. "
                    "Este monto es solo simbólico, no se realizará ningún cobro. "
                    "Pero si deseas desconectarte de Google Ads, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                    "Usa máximo 5 líneas. No repitas lo que dijo el usuario literalmente. No digas que estás leyendo el historial. Mantén el tono humano, cercano y útil, como si estuvieras charlando con un amigo."
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

        # ✅ Monto válido → guardar en hoja
        update_user_field(numero_usuario, "Requested Budget", monto_limpio)
        update_user_field(numero_usuario, "Estado Campana", "Monto Registrado")

        print(f"[LOG] Monto registrado correctamente: {monto_limpio} Bs para número: {numero_usuario}")

        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar el monto. ¿Podrías repetirlo por favor?"





















from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_monto_inversion(numero_usuario, mensaje_usuario):
    """
    Extrae el monto de inversión diaria desde el mensaje del usuario usando GPT.
    Si es válido, lo guarda en Google Sheets y continúa el flujo.
    Si no es válido, solicita nuevamente el monto de forma cálida y contextual.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear campañas publicitarias.\n"
            "Tu tarea específica es extraer únicamente el **MONTO DIARIO DE INVERSIÓN** que el usuario desea destinar a su campaña, expresado en bolivianos.\n"
            "El resultado debe ser **únicamente un número entero positivo**, sin símbolos, sin decimales, sin texto explicativo ni palabras como 'bolivianos' o 'Bs'.\n"
            "Ejemplo: si el mensaje dice 'quiero invertir 50 bolivianos al día', debes devolver únicamente: 50\n\n"
            "No devuelvas palabras como 'cincuenta', no devuelvas frases largas ni repitas la oración del usuario.\n"
            "No incluyas signos como Bs, $, puntos, comas, o espacios. Solo un número limpio y usable como monto en Google Ads.\n\n"
            "**IMPORTANTE:** Si no puedes detectar un monto válido (por ejemplo si el usuario no dijo ningún número claro), debes devolver exactamente la palabra: `NO_MONTO`.\n"
            "No expliques, no razones, no devuelvas ningún otro texto. Solo `NO_MONTO` si no se encuentra un monto claro y usable."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=10
        )

        monto_crudo = respuesta.choices[0].message.content.strip()

        if monto_crudo.upper() == "NO_MONTO":
            return volver_a_pedir_monto(numero_usuario, mensaje_usuario)

        monto_numerico = re.sub(r"[^\d]", "", monto_crudo)

        if not monto_numerico.isdigit() or int(monto_numerico) < 1:
            return volver_a_pedir_monto(numero_usuario, mensaje_usuario)

        # ✅ Monto válido → guardar y continuar
        update_user_field(numero_usuario, "Requested Budget", monto_numerico)
        update_user_field(numero_usuario, "Estado Campana", "Monto Registrado")

        print(f"[LOG] Monto diario registrado: {monto_numerico} Bs para número: {numero_usuario}")

        # 🔁 Importación perezosa para evitar error de circular import
        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar el monto de inversión. ¿Podrías escribirlo nuevamente por favor?"


def volver_a_pedir_monto(numero_usuario, mensaje_usuario):
    """
    Si el usuario no indica un monto válido, se vuelve a pedir con un mensaje claro y cálido.
    """

    historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
    historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

    prompt_reintento = [{
        "role": "system",
        "content": (
            f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios por WhatsApp.\n"
            f"Le pediste que te indique el monto que podría invertir por día en su campaña, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
            f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
            f"{historial_texto}\n"
            "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
            "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
            "'Para poder avanzar con la creación de tus anuncios, necesito saber cuánto podrías invertir por día en tu campaña. "
            "Este monto es solo simbólico, no se realizará ningún cobro. "
            "Pero si deseas desconectarte de Google Ads, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
            "Usa máximo 5 líneas. No repitas lo que dijo el usuario literalmente. No digas que estás leyendo el historial. Mantén el tono humano, cercano y útil, como si estuvieras charlando con un amigo."
        )
    }]

    prompt_reintento.extend(historial)

    respuesta = openai_client.chat.completions.create(
        model=GPT_MODEL_PRECISO,
        messages=prompt_reintento,
        temperature=TEMPERATURA_CONVERSACION,
        max_tokens=200
    )

    mensaje_reintento = respuesta.choices[0].message.content.strip()
    guardar_mensaje(numero_usuario, "assistant", mensaje_reintento)
    return mensaje_reintento
























from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
import re

def procesar_monto_inversion(numero_usuario, mensaje_usuario):
    """
    Extrae el monto de inversión diaria desde el mensaje del usuario usando GPT.
    Si es válido, lo guarda en Google Sheets y continúa el flujo.
    Si no es válido, solicita nuevamente el monto de forma cálida y contextual.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear campañas publicitarias.\n"
            "Tu tarea específica es extraer únicamente el **MONTO DIARIO DE INVERSIÓN** que el usuario desea destinar a su campaña, expresado en bolivianos.\n"
            "El resultado debe ser **únicamente un número entero positivo**, sin símbolos, sin decimales, sin texto explicativo ni palabras como 'bolivianos' o 'Bs'.\n"
            "Ejemplo: si el mensaje dice 'quiero invertir 50 bolivianos al día', debes devolver únicamente: 50\n\n"
            "No devuelvas palabras como 'cincuenta', no devuelvas frases largas ni repitas la oración del usuario.\n"
            "No incluyas signos como Bs, $, puntos, comas, o espacios. Solo un número limpio y usable como monto en Google Ads.\n\n"
            "**IMPORTANTE:** Si no puedes detectar un monto válido (por ejemplo si el usuario no dijo ningún número claro), debes devolver exactamente la palabra: `NO_MONTO`.\n"
            "No expliques, no razones, no devuelvas ningún otro texto. Solo `NO_MONTO` si no se encuentra un monto claro y usable."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]


    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=10
        )

        monto_crudo = respuesta.choices[0].message.content.strip()

        if monto_crudo.upper() == "NO_MONTO":
            return volver_a_pedir_monto(numero_usuario, mensaje_usuario)

        monto_numerico = re.sub(r"[^\d]", "", monto_crudo)

        if not monto_numerico.isdigit() or int(monto_numerico) < 1:
            return volver_a_pedir_monto(numero_usuario, mensaje_usuario)

        # ✅ Monto válido → guardar y continuar
        update_user_field(numero_usuario, "Requested Budget", monto_numerico)
        update_user_field(numero_usuario, "Estado Campana", "Monto Registrado")

        print(f"[LOG] Monto diario registrado: {monto_numerico} Bs para número: {numero_usuario}")
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar el monto de inversión. ¿Podrías escribirlo nuevamente por favor?"


def volver_a_pedir_monto(numero_usuario, mensaje_usuario):
    """
    Si el usuario no indica un monto válido, se vuelve a pedir con un mensaje claro y cálido.
    """

    historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
    historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

    prompt_reintento = [{
        "role": "system",
        "content": (
            f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios por WhatsApp.\n"
            f"Le pediste que te indique el monto que podría invertir por día en su campaña, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
            f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
            f"{historial_texto}\n"
            "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
            "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
            "'Para poder avanzar con la creación de tus anuncios, necesito saber cuánto podrías invertir por día en tu campaña. "
            "Este monto es solo simbólico, no se realizará ningún cobro. "
            "Pero si deseas desconectarte de Google Ads, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
            "Usa máximo 5 líneas. No repitas lo que dijo el usuario literalmente. No digas que estás leyendo el historial. Mantén el tono humano, cercano y útil, como si estuvieras charlando con un amigo."
        )
    }]

    prompt_reintento.extend(historial)

    respuesta = openai_client.chat.completions.create(
        model=GPT_MODEL_PRECISO,
        messages=prompt_reintento,
        temperature=TEMPERATURA_CONVERSACION,
        max_tokens=200
    )

    mensaje_reintento = respuesta.choices[0].message.content.strip()
    guardar_mensaje(numero_usuario, "assistant", mensaje_reintento)
    return mensaje_reintento
'''