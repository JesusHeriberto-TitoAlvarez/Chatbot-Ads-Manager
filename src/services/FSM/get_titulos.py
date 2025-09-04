from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_titulos_usuario(numero_usuario, mensaje_usuario):
    """
    Procesa la respuesta del usuario para extraer 3 títulos separados por '|' y registrarlos.
    Si no se detectan bien, vuelve a pedirlos amablemente.
    """

    # Paso 1: Intentar extraer los títulos
    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a los usuarios de WhatsApp a crear sus anuncios publicitarios.\n\n"
            "El usuario enviará un mensaje con 3 títulos separados por guiones (-).\n\n"
            "**Tu tarea es OBLIGATORIAMENTE:**\n"
            "- Extraer exactamente **3 títulos publicitarios**.\n"
            "- Cada título debe tener como máximo **30 caracteres**.\n"
            "- Si un título supera los 30 caracteres, debes **resumir o parafrasear ligeramente** sin inventar contenido nuevo.\n"
            "- Devuelve los títulos separados estrictamente por el símbolo `|` (sin espacios antes ni después del `|`).\n\n"
            "**Ejemplo de entrada del usuario:**\n"
            "me parece que puedo usar estos. 'Gran oferta imperdible - Compra fácil y rápida - Promoción especial por tiempo limitado.'\n\n"
            "**Ejemplo de salida correcta:**\n"
            "'Gran oferta|Compra fácil|Promoción especial'\n\n"
            "**Reglas estrictas:**\n"
            "- No agregues nuevos títulos.\n"
            "- No inventes negocios diferentes.\n"
            "- No expliques tu respuesta ni escribas mensajes adicionales.\n"
            "- Si no puedes cumplir exactamente con las instrucciones, responde únicamente con `NO_TITULOS` (en mayúsculas)."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=100
        )

        titulos_crudos = respuesta.choices[0].message.content.strip()

        if titulos_crudos.count("|") != 2:
            titulos_limpios = "NO_TITULOS"
        else:
            titulos_list = [t.strip() for t in titulos_crudos.split("|") if t.strip()]
            if any(len(t) > 30 for t in titulos_list):
                titulos_limpios = "NO_TITULOS"
            else:
                titulos_limpios = titulos_crudos

        # Paso 2: Validar resultados
        if titulos_limpios == "NO_TITULOS":
            # No se detectaron bien los títulos
            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear su anuncio.\n"
                    f"Le pediste que te envíe 3 títulos separados por guiones, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de su conversación:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando normalmente por WhatsApp.\n\n"
                    "OBLIGATORIAMENTE debes PARAFRASEAR la siguiente idea dentro del mensaje:\n"
                    "'Necesito que me envíes 3 títulos publicitarios separados por guiones, como en este ejemplo: Gran oferta - Compra fácil - Promoción especial. "
                    "Si deseas, también puedes escribir *CREAR TITULOS* en mayúsculas y yo te ayudaré a generarlos automáticamente para ti. "
                    "Y si prefieres salir del proceso, puedes escribir *SALIR* en mayúsculas.'\n\n"
                    "No repitas literal lo que dijo el usuario. No digas que estás leyendo el historial. Usa máximo 7 líneas, manteniendo un tono cálido, humano, útil y funcional."
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
            mensaje_verificado = mensaje_reintento.lower()

            # ✅ Verificación obligatoria
            if "crear titulos" not in mensaje_verificado or "salir" not in mensaje_verificado:
                mensaje_reintento = (
                    "Para continuar necesito que me envíes 3 títulos publicitarios separados por guiones, como: "
                    "Gran oferta - Compra fácil - Promoción especial. "
                    "También puedes escribir *CREAR TITULOS* en mayúsculas para ayudarte automáticamente. "
                    "Y si deseas salir del proceso, escribe *SALIR* en mayúsculas."
                )

            guardar_mensaje(numero_usuario, "assistant", mensaje_reintento)
            return mensaje_reintento


        # ✅ Títulos válidos
        update_user_field(numero_usuario, "Titles", titulos_limpios)
        update_user_field(numero_usuario, "Estado Anuncio", "Titulos Registrados")

        print(f"[LOG] Títulos extraídos correctamente: {titulos_limpios} para número: {numero_usuario}")

        # Import dinámico para evitar import circular
        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar tus títulos. ¿Podrías enviarlos nuevamente separados por guiones, por favor?"









'''
from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_titulos_usuario(numero_usuario, mensaje_usuario):
    """
    Procesa la respuesta del usuario para extraer 3 títulos separados por '|'.
    Si no se detectan bien, vuelve a pedirlos amablemente.
    """

    # Paso 1: Intentar extraer los títulos
    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a los usuarios de WhatsApp a crear sus anuncios publicitarios.\n\n"
            "El usuario te enviará un mensaje con 3 títulos separados por guiones (-).\n\n"
            "**Tu tarea es OBLIGATORIAMENTE:**\n"
            "- Extraer exactamente **3 títulos publicitarios**.\n"
            "- Cada título debe tener como máximo **30 caracteres**.\n"
            "- Si un título supera los 30 caracteres, debes **resumir o parafrasear ligeramente** sin inventar contenido nuevo.\n"
            "- Devuelve los títulos separados estrictamente por el símbolo `|` (sin espacios antes ni después del `|`).\n\n"
            "**Ejemplo de entrada del usuario:**\n"
            "me parece que puedo usar estos. 'Gran oferta imperdible - Compra fácil y rápida - Promoción especial por tiempo limitado.'\n\n"
            "**Ejemplo de salida correcta:**\n"
            "'Gran oferta|Compra fácil|Promoción especial'\n\n"
            "**Reglas estrictas:**\n"
            "- No agregues nuevos títulos.\n"
            "- No inventes negocios diferentes.\n"
            "- No expliques tu respuesta ni escribas mensajes adicionales.\n"
            "- Si no puedes cumplir exactamente con las instrucciones, responde únicamente con `NO_TITULOS` (en mayúsculas)."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=100
        )

        titulos_crudos = respuesta.choices[0].message.content.strip()

        if titulos_crudos.count("|") != 2:
            titulos_limpios = "NO_TITULOS"
        else:
            titulos_list = [t.strip() for t in titulos_crudos.split("|") if t.strip()]
            if any(len(t) > 30 for t in titulos_list):
                titulos_limpios = "NO_TITULOS"
            else:
                titulos_limpios = titulos_crudos

        # Paso 2: Validar resultados
        if titulos_limpios == "NO_TITULOS":
            # No se detectaron bien los títulos
            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios.\n"
                    f"Le pediste que enviara 3 títulos, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"Este es el historial reciente de su conversación:\n\n"
                    f"{historial_texto}\n\n"
                    "Ahora debes generar una respuesta cálida, humana y natural como si estuvieras conversando en WhatsApp.\n\n"
                    "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                    "'Para seguir avanzando, por favor envíame 3 títulos separados por guiones. Ejemplo: Gran oferta - Compra fácil - Promoción especial.'\n\n"
                    "No expliques que estás leyendo historial. Usa máximo 5 líneas, con un tono humano y de acompañamiento."
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

        # ✅ Títulos válidos
        update_user_field(numero_usuario, "Titles", titulos_limpios)
        update_user_field(numero_usuario, "Estado Anuncio", "Titulos Registrados")

        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        print(f"[LOG] Títulos extraídos correctamente: {titulos_limpios} para número: {numero_usuario}")
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar tus títulos. ¿Podrías enviarlos nuevamente separados por guiones, por favor?"

















from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_titulos_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae los títulos del mensaje usando GPT y los guarda en Google Sheets.
    Si son válidos, actualiza el estado y vuelve a ejecutar el flujo principal.
    Si son inválidos, explica con naturalidad y espera una nueva entrada.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear campañas publicitarias.\n"
            "Tu tarea específica es extraer exactamente **3 títulos publicitarios para Google Ads** a partir de un mensaje informal enviado por WhatsApp.\n"
            "El usuario enviará los títulos separados por guiones (-).\n\n"
            "Ejemplo de entrada: 'Gran oferta imperdible - Compra fácil y rápida - Promoción especial por tiempo limitado'.\n"
            "Debes devolver únicamente los 3 títulos separados con '|' de la siguiente manera:\n"
            "'Gran oferta|Compra fácil|Promoción especial'.\n\n"
            "**Reglas importantes:**\n"
            "- Cada título individual debe tener **máximo 30 caracteres**.\n"
            "- Si un título supera los 30 caracteres, **debes parafrasearlo o resumirlo ligeramente** para ajustarlo.\n"
            "- No inventes nuevos títulos. Solo adapta el contenido que el usuario haya escrito.\n"
            "- No agregues palabras nuevas que no estaban.\n"
            "- No expliques nada en tu respuesta. No devuelvas textos adicionales ni saludos.\n\n"
            "**IMPORTANTE:** Si no puedes encontrar 3 títulos claros y válidos, debes devolver exactamente la palabra `NO_TITULOS`.\n"
            "No razones, no completes, no escribas nada extra si fallas. Solo devuelve `NO_TITULOS`."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=50
        )

        titulos_crudos = respuesta.choices[0].message.content.strip()

        if titulos_crudos.strip().upper() == "NO_TITULOS":
            titulos_limpios = "NO_TITULOS"
        else:
            titulos_limpios = re.sub(r"[\"'´`<>]", "", titulos_crudos.strip())

        if titulos_limpios.upper() == "NO_TITULOS" or titulos_limpios.count("|") != 2:
            # No se detectaron correctamente los títulos
            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear su anuncio.\n"
                    f"Le pediste que te envíe 3 títulos separados por guiones, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de su conversación:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando normalmente por WhatsApp.\n\n"
                    "OBLIGATORIAMENTE debes PARAFRASEAR la siguiente idea dentro del mensaje:\n"
                    "'Necesito que me envíes 3 títulos publicitarios separados por guiones, como en este ejemplo: Gran oferta - Compra fácil - Promoción especial. "
                    "Si deseas, también puedes escribir CREAR TITULOS en mayúsculas y yo te ayudaré a generarlos automáticamente para ti. "
                    "Y si prefieres salir del proceso, puedes escribir SALIR en mayúsculas.'\n\n"
                    "No repitas literal lo que dijo el usuario. No digas que estás leyendo el historial. Usa máximo 7 líneas, manteniendo un tono cálido, humano, útil y funcional."
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

        # ✅ Títulos válidos
        update_user_field(numero_usuario, "Titles", titulos_limpios)
        update_user_field(numero_usuario, "Estado Anuncio", "Titulos Registrados")

        print(f"[LOG] Títulos registrados correctamente: {titulos_limpios} para número: {numero_usuario}")

        from src.services.FSM.titles.flujo_creacion_titulos import ejecutar_flujo_creacion_titulos
        return ejecutar_flujo_creacion_titulos(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar tus títulos. ¿Podrías enviarlos nuevamente por favor?"















from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_titulos_usuario(numero_usuario, mensaje_usuario):
    """
    Extrae los títulos del mensaje usando GPT y los guarda en Google Sheets.
    Si son válidos, actualiza el estado y vuelve a ejecutar el flujo principal.
    Si son inválidos, explica con naturalidad y espera una nueva entrada.
    """

    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a las personas a crear campañas publicitarias.\n"
            "Tu tarea específica es extraer exactamente **3 títulos publicitarios para Google Ads** a partir de un mensaje informal enviado por WhatsApp.\n"
            "El usuario enviará los títulos separados por guiones (-).\n\n"
            "Ejemplo de entrada: 'Gran oferta imperdible - Compra fácil y rápida - Promoción especial por tiempo limitado'.\n"
            "Debes devolver únicamente los 3 títulos separados con '|' de la siguiente manera:\n"
            "'Gran oferta|Compra fácil|Promoción especial'.\n\n"
            "**Reglas importantes:**\n"
            "- Cada título individual debe tener **máximo 30 caracteres**.\n"
            "- Si un título supera los 30 caracteres, **debes parafrasearlo o resumirlo ligeramente** para ajustarlo.\n"
            "- No inventes nuevos títulos. Solo adapta el contenido que el usuario haya escrito.\n"
            "- No agregues palabras nuevas que no estaban.\n"
            "- No expliques nada en tu respuesta. No devuelvas textos adicionales ni saludos.\n\n"
            "**IMPORTANTE:** Si no puedes encontrar 3 títulos claros y válidos, debes devolver exactamente la palabra `NO_TITULOS`.\n"
            "No razones, no completes, no escribas nada extra si fallas. Solo devuelve `NO_TITULOS`."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]


    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=50
        )

        titulos_crudos = respuesta.choices[0].message.content.strip()

        if titulos_crudos.strip().upper() == "NO_TITULOS":
            titulos_limpios = "NO_TITULOS"
        else:
            titulos_limpios = re.sub(r"[\"'´`<>]", "", titulos_crudos.strip())

        if titulos_limpios.upper() == "NO_TITULOS" or titulos_limpios.count("|") != 2:
            # No se detectaron correctamente los títulos
            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear su anuncio.\n"
                    f"Le pediste que te envíe 3 títulos separados por guiones, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de su conversación:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando normalmente por WhatsApp.\n\n"
                    "OBLIGATORIAMENTE debes PARAFRASEAR la siguiente idea dentro del mensaje:\n"
                    "'Necesito que me envíes 3 títulos publicitarios separados por guiones, como en este ejemplo: Gran oferta - Compra fácil - Promoción especial. "
                    "Si deseas, también puedes escribir CREAR TITULOS en mayúsculas y yo te ayudaré a generarlos automáticamente para ti. "
                    "Y si prefieres salir del proceso, puedes escribir SALIR en mayúsculas.'\n\n"
                    "No repitas literal lo que dijo el usuario. No digas que estás leyendo el historial. Usa máximo 7 líneas, manteniendo un tono cálido, humano, útil y funcional."
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

        # ✅ Títulos válidos
        update_user_field(numero_usuario, "Titles", titulos_limpios)
        update_user_field(numero_usuario, "Estado Anuncio", "Titulos Registrados")

        print(f"[LOG] Títulos registrados correctamente: {titulos_limpios} para número: {numero_usuario}")

        from src.services.FSM.flujo_creacion_anuncio import ejecutar_flujo_creacion_anuncio
        return ejecutar_flujo_creacion_anuncio(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar tus títulos. ¿Podrías enviarlos nuevamente por favor?"
'''