from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_nombre_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del mensaje usando GPT y lo guarda en Google Sheets.
    Si es válido, actualiza el estado y vuelve a ejecutar el flujo principal.
    Si es inválido, explica con naturalidad y espera una nueva entrada.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear anuncios.\n"
            "Tu tarea específica es extraer únicamente el **NOMBRE PROPIO DEL USUARIO**.\n"
            "Puede tener como máximo **dos palabras**, si ambas son nombres propios válidos de persona (como 'José Miguel').\n"
            "Ejemplo: si el mensaje dice 'me llamo Heriberto Tito', debes devolver: 'Heriberto Tito'.\n"
            "Si el mensaje dice 'me llamo Jesús Heriberto Tito Álvarez', debes devolver: 'Jesús Heriberto'.\n"
            "No devuelvas apellidos, no devuelvas nombres de empresas, ni aceptes frases que no sean un nombre humano real.\n"
            "No incluyas saludos, explicaciones, signos ni comillas. Solo el nombre limpio, listo para usar en una conversación.\n"
            "El resultado debe estar capitalizado y sin errores ortográficos graves.\n"
            "**IMPORTANTE:** Si no puedes detectar un nombre válido de persona, debes devolver exactamente la palabra: NO_NAME\n"
            "No expliques, no inventes, no rellenes. Solo devuelve NO_NAME si no encuentras un nombre apropiado."
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

        nombre_crudo = respuesta.choices[0].message.content.strip()
        
        if nombre_crudo.strip().upper() == "NO_NAME":
            nombre_limpio = "NO_NAME"
        else:
            nombre_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ ]", "", nombre_crudo).strip().title()
            palabras = nombre_limpio.split()
            nombre_limpio = " ".join(palabras[:2])  # máximo dos palabras



        if nombre_limpio.upper() == "NO_NAME" or len(nombre_limpio) < 2:

            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios.\n"
                    f"Le pediste que te diga su nombre, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
                    "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
                    "'Para poder continuar con la creación de sus anuncios nos debe indicar su nombre por favor. "
                    "Pero en caso que desee desconectarse de Google Ads debe escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                    "Usa máximo 5 líneas. No repitas literalmente lo que dijo el usuario. Mantén el tono humano y útil."
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

        # ✅ Nombre válido
        update_user_field(numero_usuario, "User Name", nombre_limpio)
        update_user_field(numero_usuario, "Estado Campana", "Nombre Registrado")

        # 🧠 Mostrar en logs, no en Firestore
        print(f"[LOG] Nombre registrado correctamente: {nombre_limpio} para número: {numero_usuario}")

        # 🧠 Importar aquí para evitar ciclo
        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar tu nombre. ¿Podrías repetirlo por favor?"










'''
from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_nombre_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del mensaje usando GPT y lo guarda en Google Sheets.
    Si es válido, actualiza el estado y vuelve a ejecutar el flujo principal.
    Si es inválido, explica con naturalidad y espera una nueva entrada.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear anuncios.\n"
            "Tu tarea específica es extraer únicamente el **NOMBRE PROPIO DEL USUARIO**, y debe ser **una sola palabra limpia**.\n"
            "Ejemplo: si el mensaje dice 'me llamo Heriberto Tito', debes devolver solo: 'Heriberto'.\n"
            "No devuelvas apellidos, no devuelvas nombres de empresas, no aceptes errores ortográficos graves, ni frases que no sean un nombre humano real.\n"
            "No incluyas saludos, explicaciones, signos ni comillas. Solo una palabra con formato de nombre propio capitalizado.\n"
            "Si el mensaje incluye múltiples palabras, selecciona solo la primera que sea un nombre propio claro. Ignora lo demás.\n"
            "El resultado debe ser 100 porciento limpio y usable como nombre personal en una conversación seria."
            "**IMPORTANTE:** Si no puedes detectar un nombre válido de persona, debes devolver exactamente la palabra: `NO_NAME`.\n"
            "No expliques, no inventes, no rellenes. Solo devuelve `NO_NAME` si no encuentras un nombre apropiado."
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

        nombre_crudo = respuesta.choices[0].message.content.strip()
        nombre_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]", "", nombre_crudo.split()[0]).title()

        if nombre_limpio.upper() == "NO_NAME" or len(nombre_limpio) < 2:

            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios.\n"
                    f"Le pediste que te diga su nombre, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de la conversación entre ustedes:\n\n"
                    f"{''.join([f'{m['role']}: {m['content']}\n' for m in historial])}\n"
                    "Ahora debes generar una respuesta breve, cálida y natural a ese mensaje, como si estuvieras hablando por WhatsApp.\n\n"
                    "IMPORTANTE: Además de esa respuesta, debes agregar OBLIGATORIAMENTE y de forma PARAFRASEADA el siguiente mensaje:\n"
                    "'Para poder continuar con la creación de sus anuncios nos debe indicar su nombre por favor. "
                    "Pero en caso que desee desconectarse de Google Ads debe escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                    "Usa máximo 5 líneas. No repitas literalmente lo que dijo el usuario. Mantén el tono humano y útil."
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
    
        # ✅ Nombre válido
        update_user_field(numero_usuario, "User Name", nombre_limpio)
        update_user_field(numero_usuario, "Estado Campana", "Nombre Registrado")

        # 🧠 Mostrar en logs, no en Firestore
        print(f"[LOG] Nombre registrado correctamente: {nombre_limpio} para número: {numero_usuario}")

        # 🧠 Importar aquí para evitar ciclo
        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)


    except Exception:
        return "Hubo un problema al procesar tu nombre. ¿Podrías repetirlo por favor?"

















from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
import re

def procesar_nombre_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del mensaje usando GPT y lo guarda en Google Sheets y Firestore.
    Si no se detecta un nombre válido, vuelve a pedirlo de forma natural y amigable.
    Si se detecta correctamente, actualiza el estado y continúa el flujo.
    """

    # Paso 1: Intentar extraer el nombre
    prompt = [
        {"role": "system", "content": (
            "Eres un asistente experto en extraer nombres de personas a partir de mensajes informales de WhatsApp.\n"
            "Cuando alguien escribe 'me llamo Heriberto Tito' o 'soy la karla', debes extraer únicamente el PRIMER nombre propio en forma clara, corregida y capitalizada.\n"
            "Si hay varios nombres (como 'Luis Fernando' o 'Ana María'), devuelve solo el primer nombre.\n"
            "No devuelvas saludos, explicaciones ni frases adicionales. Solo una palabra: el nombre limpio y sin comillas ni puntuación.\n"
            "No uses nombres que parezcan apodos, emojis o texto sin sentido. El resultado debe ser un nombre humano real, en una sola palabra."
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

        nombre_crudo = respuesta.choices[0].message.content.strip()
        nombre_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]", "", nombre_crudo.split()[0]).title()

        if len(nombre_limpio) < 2 or "nombre" in nombre_limpio.lower():
            # ❌ Nombre inválido → pedir nuevamente el nombre de forma natural
            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

            prompt_reintento = [{
                "role": "system",
                "content": (
                    "Eres un chatbot amable y profesional que está guiando a un usuario a crear una campaña en Google Ads.\n"
                    "Ya le pediste su nombre, pero el mensaje que recibiste no parece contener un nombre válido.\n"
                    "PARAFRASEA dentro de un mensaje cálido y humano algo como:\n\n"
                    "'En este momento estoy conectado directamente con Google Ads. Para continuar con la creación de tu campaña, necesito tu nombre por favor. "
                    "Si deseas desconectarte y salir del proceso, puedes escribir SALIR (en mayúsculas y sin signos) en cualquier momento.'\n\n"
                    "Combina esto con los últimos mensajes del historial. Habla como si estuvieras en una conversación real por WhatsApp. No repitas lo que dijo el usuario. Usa máximo 5 líneas."
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

        # ✅ Nombre válido → guardar en Google Sheets y avanzar
        update_user_field(numero_usuario, "User Name", nombre_limpio)
        update_user_field(numero_usuario, "Estado Campana", "Nombre Registrado")

        guardar_mensaje(numero_usuario, "system", f"Nombre registrado: {nombre_limpio}")

        # 🔁 Volver a ejecutar flujo principal
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar tu nombre. ¿Podrías repetirlo por favor?"













from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_nombre_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del mensaje usando GPT y lo guarda en Google Sheets y Firestore.
    Si no se detecta un nombre válido, vuelve a pedirlo de forma natural y amigable.
    """

    # Paso 1: Intentar extraer el nombre
    prompt = [
        {"role": "system", "content": (
            "Eres un asistente experto en extraer nombres de personas a partir de mensajes informales de WhatsApp.\n"
            "Cuando alguien escribe 'me llamo Heriberto Tito' o 'soy la karla', debes extraer únicamente el PRIMER nombre propio en forma clara, corregida y capitalizada.\n"
            "Si hay varios nombres (como 'Luis Fernando' o 'Ana María'), devuelve solo el primer nombre.\n"
            "No devuelvas saludos, explicaciones ni frases adicionales. Solo una palabra: el nombre limpio y sin comillas ni puntuación.\n"
            "No uses nombres que parezcan apodos, emojis o texto sin sentido. El resultado debe ser un nombre humano real, en una sola palabra."
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

        nombre_crudo = respuesta.choices[0].message.content.strip()
        nombre_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]", "", nombre_crudo.split()[0]).title()

        if len(nombre_limpio) < 2 or "nombre" in nombre_limpio.lower():
            # Nombre inválido → pedir nuevamente el nombre de forma natural
            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

            prompt_reintento = [{
                "role": "system",
                "content": (
                    "Eres un chatbot amable y profesional que está guiando a un usuario a crear una campaña en Google Ads.\n"
                    "Ya le pediste su nombre, pero el mensaje que recibiste no parece contener un nombre válido.\n"
                    "PARAFRASEA dentro de un mensaje cálido y humano algo como:\n\n"
                    "'En este momento estoy conectado directamente con Google Ads. Para continuar con la creación de tu campaña, necesito tu nombre por favor. "
                    "Si deseas desconectarte y salir del proceso, puedes escribir SALIR (en mayúsculas y sin signos) en cualquier momento.'\n\n"
                    "Combina esto con los últimos mensajes del historial. Habla como si estuvieras en una conversación real por WhatsApp. No repitas lo que dijo el usuario. Usa máximo 5 líneas."
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

        # Nombre válido → guardar y finalizar
        update_user_field(numero_usuario, "User Name", nombre_limpio)
        update_user_field(numero_usuario, "Estado Campana", "Nombre Registrado")

        # Guardar confirmación silenciosa en Firestore (opcional)
        guardar_mensaje(numero_usuario, "system", f"Nombre registrado: {nombre_limpio}")

        return f"Gracias {nombre_limpio}, tu nombre ha sido registrado correctamente. "

    except Exception:
        return "Hubo un problema al procesar tu nombre. ¿Podrías repetirlo por favor?"


















from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_nombre_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del mensaje usando GPT y lo guarda en Google Sheets y Firestore.
    Si no se detecta un nombre válido, vuelve a pedirlo de forma natural y amigable.
    """

    # Paso 1: Intentar extraer el nombre
    prompt = [
        {"role": "system", "content": (
            "Eres un asistente experto en extraer nombres de personas a partir de mensajes informales de WhatsApp.\n"
            "Cuando alguien escribe 'me llamo Heriberto Tito' o 'soy la karla', debes extraer únicamente el PRIMER nombre propio en forma clara, corregida y capitalizada.\n"
            "Si hay varios nombres (como 'Luis Fernando' o 'Ana María'), devuelve solo el primer nombre.\n"
            "No devuelvas saludos, explicaciones ni frases adicionales. Solo una palabra: el nombre limpio y sin comillas ni puntuación.\n"
            "No uses nombres que parezcan apodos, emojis o texto sin sentido. El resultado debe ser un nombre humano real, en una sola palabra."
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

        nombre_crudo = respuesta.choices[0].message.content.strip()
        nombre_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]", "", nombre_crudo.split()[0]).title()

        if len(nombre_limpio) < 2 or "nombre" in nombre_limpio.lower():
            return volver_a_pedir_nombre_usuario(numero_usuario)

        # Paso 2: Guardar nombre y actualizar estado
        update_user_field(numero_usuario, "User Name", nombre_limpio)
        update_user_field(numero_usuario, "Estado Campana", "Nombre Registrado")

        # Paso 3: Generar respuesta para pedir nombre de empresa
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        prompt_respuesta = [{"role": "system", "content": (
            f"Eres un chatbot conversacional que ya recibió el nombre '{nombre_limpio}' del usuario.\n"
            "PARAFRASEA dentro de un mensaje cálido, natural y en tono de WhatsApp:\n\n"
            "'Gracias por decirme tu nombre. Ahora, ¿podrías decirme cómo se llama tu empresa, negocio o emprendimiento para ayudarte con la campaña?'\n\n"
            "No suenes forzado ni repitas textos. Usa máximo 5 líneas. Combina esto naturalmente con el historial reciente. "
            "Debes sonar como una persona amable que conversa fluidamente con el usuario."
        )}]
        prompt_respuesta.extend(historial)

        respuesta_dinamica = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt_respuesta,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        mensaje_final = respuesta_dinamica.choices[0].message.content.strip()
        guardar_mensaje(numero_usuario, "assistant", mensaje_final)
        return mensaje_final

    except Exception:
        return "Hubo un problema al procesar tu nombre. ¿Podrías repetirlo por favor?"

def volver_a_pedir_nombre_usuario(numero_usuario):
    """
    Si no se detecta un nombre válido, se vuelve a pedir de forma clara y natural,
    recordando que puede salir con SALIR (en mayúsculas y sin signos).
    """
    historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

    prompt_reintento = [{
        "role": "system",
        "content": (
            "Eres un chatbot amable y profesional que está guiando a un usuario a crear una campaña en Google Ads.\n"
            "Ya le pediste su nombre, pero el mensaje que recibiste no parece contener un nombre válido.\n"
            "PARAFRASEA dentro de un mensaje cálido y humano algo como:\n\n"
            "'En este momento estoy conectado directamente con Google Ads. Para continuar con la creación de tu campaña, necesito tu nombre por favor. "
            "Si deseas desconectarte y salir del proceso, puedes escribir SALIR (en mayúsculas y sin signos) en cualquier momento.'\n\n"
            "Combina esto con los últimos mensajes del historial. Habla como si estuvieras en una conversación real por WhatsApp. No repitas lo que dijo el usuario. Usa máximo 5 líneas."
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

def procesar_nombre_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del mensaje usando GPT y lo guarda en Google Sheets y Firestore.
    Luego genera un mensaje dinámico para pedir el nombre del negocio.
    """

    # Paso 1: Extraer nombre del mensaje del usuario
    prompt = [
        {"role": "system", "content": (
            "Eres un asistente experto en extraer nombres de personas a partir de mensajes informales de WhatsApp.\n"
            "Cuando alguien escribe 'me llamo Heriberto Tito' o 'soy la karla', debes extraer únicamente el PRIMER nombre propio en forma clara, corregida y capitalizada.\n"
            "Si hay varios nombres (como 'Luis Fernando' o 'Ana María'), devuelve solo el primer nombre.\n"
            "No devuelvas saludos, explicaciones ni frases adicionales. Solo una palabra: el nombre limpio y sin comillas ni puntuación.\n"
            "No uses nombres que parezcan apodos, emojis o texto sin sentido. El resultado debe ser un nombre humano real, en una sola palabra."
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

        nombre_crudo = respuesta.choices[0].message.content.strip()
        nombre_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]", "", nombre_crudo.split()[0]).title()

        if len(nombre_limpio) < 2 or "nombre" in nombre_limpio.lower():
            return volver_a_pedir_nombre_usuario(numero_usuario)

        # Paso 2: Guardar nombre en Google Sheets
        update_user_field(numero_usuario, "User Name", nombre_limpio)
        update_user_field(numero_usuario, "Estado Campana", "Nombre Registrado")

        # Paso 3: Leer historial reciente (3 mensajes por tipo)
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

        # Paso 4: Construir prompt dinámico con historial y pedir nombre del negocio
        prompt_respuesta = [{"role": "system", "content": (
            f"Eres un chatbot conversacional que ya recibió el nombre '{nombre_limpio}' del usuario.\n"
            "PARAFRASEA dentro de un mensaje cálido, natural y en tono de WhatsApp:\n\n"
            "'Gracias por decirme tu nombre. Ahora, ¿podrías decirme cómo se llama tu empresa, negocio o emprendimiento para ayudarte con la campaña?'\n\n"
            "No suenes forzado ni repitas textos. Usa máximo 5 líneas. Combina esto naturalmente con el historial reciente. "
            "Debes sonar como una persona amable que conversa fluidamente con el usuario."
        )}]
        prompt_respuesta.extend(historial)

        respuesta_dinamica = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt_respuesta,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        mensaje_final = respuesta_dinamica.choices[0].message.content.strip()

        # Paso 5: Guardar mensaje final en Firestore y retornar
        guardar_mensaje(numero_usuario, "assistant", mensaje_final)
        return mensaje_final

    except Exception as e:
        return "Hubo un problema al procesar tu nombre. ¿Podrías repetirlo por favor?"


def volver_a_pedir_nombre_empresa(numero_usuario):
    """
    En caso de que el usuario no haya proporcionado un nombre válido de empresa, se vuelve a pedir con contexto.
    """
    historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

    prompt_reintento = [{"role": "system", "content": (
        "Eres un chatbot amable que está guiando a un usuario para crear su campaña publicitaria en Google Ads.\n"
        "Ya has recibido su nombre, pero su siguiente mensaje no parece ser el nombre de su empresa o negocio.\n"
        "PARAFRASEA dentro de una conversación natural algo como:\n\n"
        "'Gracias, pero para continuar necesito saber cómo se llama tu empresa o emprendimiento. También puedes escribir SALIR en mayúsculas si deseas cancelar el proceso.'\n\n"
        "No suenes forzado. Usa un tono cálido y humano, como si hablaras por WhatsApp. Combina esto con los últimos mensajes del historial para mantener naturalidad."
    )}]
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


def volver_a_pedir_nombre_usuario(numero_usuario):
    """
    En caso de que el usuario no haya proporcionado un nombre válido, se vuelve a pedir con contexto y opción de SALIR.
    """
    historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

    prompt_reintento_nombre = [{
        "role": "system",
        "content": (
            "Eres un chatbot amable y profesional que está guiando a un usuario a crear una campaña en Google Ads.\n"
            "Ya le pediste su nombre, pero el mensaje que recibiste no parece contener un nombre válido.\n"
            "PARAFRASEA dentro de un mensaje cálido y humano algo como:\n\n"
            "'En este momento estoy conectado directamente con Google Ads. Para continuar con la creación de tu campaña, necesito tu nombre por favor. "
            "Si deseas hacerme otra pregunta, puedes escribir SALIR en mayúsculas y así podré desconectarme de Google Ads para ayudarte con otras consultas.'\n\n"
            "Combina esto con los últimos mensajes del historial. Habla como si estuvieras en una conversación real por WhatsApp. No repitas lo que dijo el usuario. Usa máximo 5 líneas."
        )
    }]
    prompt_reintento_nombre.extend(historial)

    respuesta = openai_client.chat.completions.create(
        model=GPT_MODEL_PRECISO,
        messages=prompt_reintento_nombre,
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

def procesar_nombre_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del mensaje usando GPT y lo guarda en Google Sheets y Firestore.
    Luego genera un mensaje dinámico para pedir el nombre del negocio.
    """

    # Paso 1: Extraer nombre del mensaje del usuario
    prompt = [
        {"role": "system", "content": (
            "Eres un asistente experto en extraer nombres de personas a partir de mensajes informales de WhatsApp.\n"
            "Cuando alguien escribe 'me llamo Heriberto Tito' o 'soy la karla', debes extraer únicamente el PRIMER nombre propio en forma clara, corregida y capitalizada.\n"
            "Si hay varios nombres (como 'Luis Fernando' o 'Ana María'), devuelve solo el primer nombre.\n"
            "No devuelvas saludos, explicaciones ni frases adicionales. Solo una palabra: el nombre limpio y sin comillas ni puntuación.\n"
            "No uses nombres que parezcan apodos, emojis o texto sin sentido. El resultado debe ser un nombre humano real, en una sola palabra."
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

        nombre_crudo = respuesta.choices[0].message.content.strip()
        nombre_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]", "", nombre_crudo.split()[0]).title()

        if len(nombre_limpio) < 2 or "nombre" in nombre_limpio.lower():
            return "Gracias. No logré identificar bien tu nombre. ¿Podrías repetirlo con claridad por favor?"

        # Paso 2: Guardar nombre en Google Sheets
        update_user_field(numero_usuario, "User Name", nombre_limpio)
        update_user_field(numero_usuario, "Estado Campana", "Nombre Registrado")

        # Paso 3: Leer historial reciente (3 mensajes por tipo)
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

        # Paso 4: Construir prompt dinámico con historial y pedir nombre del negocio
        prompt_respuesta = [{"role": "system", "content": (
            f"Eres un chatbot conversacional que ya recibió el nombre '{nombre_limpio}' del usuario.\n"
            "PARAFRASEA dentro de un mensaje cálido, natural y en tono de WhatsApp:\n\n"
            "'Gracias por decirme tu nombre. Ahora, ¿podrías decirme cómo se llama tu empresa, negocio o emprendimiento para ayudarte con la campaña?'\n\n"
            "No suenes forzado ni repitas textos. Usa máximo 5 líneas. Combina esto naturalmente con el historial reciente. "
            "Debes sonar como una persona amable que conversa fluidamente con el usuario."
        )}]
        prompt_respuesta.extend(historial)

        respuesta_dinamica = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt_respuesta,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        mensaje_final = respuesta_dinamica.choices[0].message.content.strip()

        # Paso 5: Guardar mensaje final en Firestore y retornar
        guardar_mensaje(numero_usuario, "assistant", mensaje_final)
        return mensaje_final

    except Exception as e:
        return "Hubo un problema al procesar tu nombre. ¿Podrías repetirlo por favor?"


def volver_a_pedir_nombre_empresa(numero_usuario):
    """
    En caso de que el usuario no haya proporcionado un nombre válido de empresa, se vuelve a pedir con contexto.
    """
    historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

    prompt_reintento = [{"role": "system", "content": (
        "Eres un chatbot amable que está guiando a un usuario para crear su campaña publicitaria en Google Ads.\n"
        "Ya has recibido su nombre, pero su siguiente mensaje no parece ser el nombre de su empresa o negocio.\n"
        "PARAFRASEA dentro de una conversación natural algo como:\n\n"
        "'Gracias, pero para continuar necesito saber cómo se llama tu empresa o emprendimiento. También puedes escribir SALIR en mayúsculas si deseas cancelar el proceso.'\n\n"
        "No suenes forzado. Usa un tono cálido y humano, como si hablaras por WhatsApp. Combina esto con los últimos mensajes del historial para mantener naturalidad."
    )}]
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























from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_nombre_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae el nombre del mensaje usando GPT y lo guarda en Google Sheets y Firestore.
    Luego genera un mensaje dinámico para pedir el nombre del negocio.
    """

    # Paso 1: Extraer nombre del mensaje del usuario
    prompt = [
        {"role": "system", "content": (
            "Eres un asistente experto en extraer nombres propios de mensajes informales de WhatsApp.\n"
            "Dado un mensaje como 'me llamo luissss' o 'soy la karla', debes responder únicamente con el nombre corregido y capitalizado.\n"
            "No devuelvas saludos, explicaciones ni frases adicionales. Solo el nombre limpio, sin adornos ni comillas."
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

        nombre_crudo = respuesta.choices[0].message.content.strip()
        nombre_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\\s\\-]", "", nombre_crudo).strip().title()

        if len(nombre_limpio) < 2 or "nombre" in nombre_limpio.lower():
            return "Gracias. No logré identificar bien tu nombre. ¿Podrías repetirlo con claridad por favor?"

        # Paso 2: Guardar nombre en Google Sheets
        update_user_field(numero_usuario, "User Name", nombre_limpio)
        update_user_field(numero_usuario, "Estado Campana", "nombre registrado")

        # Paso 3: Leer historial reciente (2 mensajes por tipo)
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)

        # Paso 4: Construir prompt dinámico con historial y pedir nombre del negocio
        prompt_respuesta = [{"role": "system", "content": (
            f"Eres un asistente conversacional que ya recibió el nombre '{nombre_limpio}' del usuario. "
            "Analiza el historial de conversación y genera un mensaje cálido, corto y natural como si hablaras por WhatsApp. "
            "Dale las gracias por su nombre y pídele que ahora indique el nombre de su empresa o negocio. "
            "No seas robótico. Usa máximo 5 líneas y mantén un tono amable y conversacional."
        )}]
        prompt_respuesta.extend(historial)

        respuesta_dinamica = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt_respuesta,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        mensaje_final = respuesta_dinamica.choices[0].message.content.strip()

        # Paso 5: Guardar mensaje final en Firestore y retornar
        guardar_mensaje(numero_usuario, "assistant", mensaje_final)
        return mensaje_final

    except Exception as e:
        return "Hubo un problema al procesar tu nombre. ¿Podrías repetirlo por favor?"
'''