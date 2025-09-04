from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_generacion_titulos(numero_usuario, mensaje_usuario):
    """
    Procesa la respuesta del usuario para generar 3 títulos publicitarios de máximo 30 caracteres.
    Si no se detectan bien, vuelve a pedir amablemente más información.
    """

    # Paso 1: Intentar generar los títulos
    try:
        prompt = [
            {"role": "system", "content": (
                "Eres un chatbot profesional conectado con Google Ads especializado en crear títulos publicitarios breves, claros y atractivos para campañas en línea.\n"
                "El usuario te proporcionará una breve descripción de su negocio y su objetivo principal.\n\n"
                "**Tu tarea es OBLIGATORIAMENTE:**\n"
                "- Generar exactamente **3 títulos** basados en la información dada.\n"
                "- Cada título debe tener como máximo **30 caracteres**.\n"
                "- Si el contenido del usuario es muy extenso, debes **resumir o parafrasear creativamente** sin inventar información nueva.\n"
                "- Separa los títulos usando el símbolo `|` (barra vertical) **sin espacios extra**.\n"
                "- No expliques, no agregues comentarios, no completes con ejemplos adicionales, no inventes temas nuevos.\n"
                "- Solo responde los 3 títulos, unidos por `|`.\n\n"
                "**IMPORTANTE:**\n"
                "- Si no puedes identificar claramente 3 títulos válidos respetando las reglas anteriores, debes devolver exactamente la palabra: `NO_TITULOS`.\n"
                "- No improvises si no puedes cumplir las reglas.\n\n"
                "**Ejemplo de entrada:** 'Tengo una zapatería y quiero atraer más clientes.'\n"
                "**Ejemplo de salida correcta:** 'Zapatos en oferta|Compra fácil|Descuentos hoy'"
            )},
            {"role": "user", "content": mensaje_usuario}
        ]

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=100
        )

        titulos_crudos = respuesta.choices[0].message.content.strip()

    except Exception:
        return "Hubo un problema al generar tus títulos. ¿Podrías describirme nuevamente tu negocio y objetivo, por favor}?"

    # Paso 2: Procesar títulos fuera del try
    if titulos_crudos.count("|") != 2:
        titulos_limpios = "NO_TITULOS"
    else:
        titulos_list = [t.strip() for t in titulos_crudos.split("|") if t.strip()]
        if any(len(t) > 30 for t in titulos_list):
            titulos_limpios = "NO_TITULOS"
        else:
            titulos_limpios = titulos_crudos

    if titulos_limpios == "NO_TITULOS":
        # No se detectaron bien los títulos
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

        prompt_reintento = [{
            "role": "system",
            "content": (
                f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios.\n"
                f"Le pediste que describiera su negocio y su objetivo, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                f"Este es el historial reciente de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Para ayudarte mejor, necesito que me cuentes brevemente a qué se dedica tu negocio y cuál es tu objetivo principal con estos anuncios. "
                "Y si deseas salir del proceso, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                "No repitas literal lo que dijo el usuario. No expliques que estás leyendo historial. Usa máximo 5 líneas, manteniendo un tono humano, cálido y de acompañamiento."
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
    update_user_field(numero_usuario, "Estado Anuncio", "Titulos Generados")

    print(f"[LOG] Títulos generados correctamente: {titulos_limpios} para número: {numero_usuario}")

    # Importar dinámicamente para evitar importación circular
    from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
    return ejecutar_flujo_creacion_campana(numero_usuario)




'''
from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
import re

def procesar_generacion_titulos(numero_usuario, mensaje_usuario):
    """
    Procesa la respuesta del usuario para generar 3 títulos publicitarios de máximo 30 caracteres.
    Si no se detectan bien, vuelve a pedir amablemente más información.
    """

    # Paso 1: Intentar generar los títulos
    try:
        prompt = [
            {"role": "system", "content": (
                "Eres un chatbot profesional conectado con Google Ads especializado en crear títulos publicitarios breves, claros y atractivos para campañas en línea.\n"
                "El usuario te proporcionará una breve descripción de su negocio y su objetivo principal.\n\n"
                "**Tu tarea es OBLIGATORIAMENTE:**\n"
                "- Generar exactamente **3 títulos** basados en la información dada.\n"
                "- Cada título debe tener como máximo **30 caracteres**.\n"
                "- Si el contenido del usuario es muy extenso, debes **resumir o parafrasear creativamente** sin inventar información nueva.\n"
                "- Separa los títulos usando el símbolo `|` (barra vertical) **sin espacios extra**.\n"
                "- No expliques, no agregues comentarios, no completes con ejemplos adicionales, no inventes temas nuevos.\n"
                "- Solo responde los 3 títulos, unidos por `|`.\n\n"
                "**IMPORTANTE:**\n"
                "- Si no puedes identificar claramente 3 títulos válidos respetando las reglas anteriores, debes devolver exactamente la palabra: `NO_TITULOS`.\n"
                "- No improvises si no puedes cumplir las reglas.\n\n"
                "**Ejemplo de entrada:** 'Tengo una zapatería y quiero atraer más clientes.'\n"
                "**Ejemplo de salida correcta:** 'Zapatos en oferta|Compra fácil|Descuentos hoy'"
            )},
            {"role": "user", "content": mensaje_usuario}
        ]

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=100
        )

        titulos_crudos = respuesta.choices[0].message.content.strip()

    except Exception:
        return "Hubo un problema al generar tus títulos. ¿Podrías describirme nuevamente tu negocio y objetivo, por favor}?"

    # Paso 2: Procesar títulos fuera del try
    if titulos_crudos.count("|") != 2:
        titulos_limpios = "NO_TITULOS"
    else:
        titulos_list = [t.strip() for t in titulos_crudos.split("|") if t.strip()]
        if any(len(t) > 30 for t in titulos_list):
            titulos_limpios = "NO_TITULOS"
        else:
            titulos_limpios = titulos_crudos

    if titulos_limpios == "NO_TITULOS":
        # No se detectaron bien los títulos
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

        prompt_reintento = [{
            "role": "system",
            "content": (
                f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario a crear sus anuncios.\n"
                f"Le pediste que describiera su negocio y su objetivo, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                f"Este es el historial reciente de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Para ayudarte mejor, necesito que me cuentes brevemente a qué se dedica tu negocio y cuál es tu objetivo principal con estos anuncios. "
                "Y si deseas salir del proceso, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                "No repitas literal lo que dijo el usuario. No expliques que estás leyendo historial. Usa máximo 5 líneas, manteniendo un tono humano, cálido y de acompañamiento."
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
    update_user_field(numero_usuario, "Estado Anuncio", "Titulos Generados")

    print(f"[LOG] Títulos generados correctamente: {titulos_limpios} para número: {numero_usuario}")

    # Correcta llamada al flujo real (flujo_creacion_campana)
    return ejecutar_flujo_creacion_campana(numero_usuario)



























from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_generacion_titulos(numero_usuario, mensaje_usuario):
    """
    Procesa la respuesta del usuario para generar 3 títulos publicitarios de máximo 30 caracteres.
    Si no se detectan bien, vuelve a pedir amablemente más información.
    """

    # Paso 1: Intentar generar los títulos
    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads especializado en crear títulos publicitarios breves, claros y atractivos para campañas en línea.\n"
            "El usuario te proporcionará una breve descripción de su negocio y su objetivo principal.\n\n"
            "**Tu tarea es OBLIGATORIAMENTE:**\n"
            "- Generar exactamente **3 títulos** basados en la información dada.\n"
            "- Cada título debe tener como máximo **30 caracteres**.\n"
            "- Si el contenido del usuario es muy extenso, debes **resumir o parafrasear creativamente** sin inventar información nueva.\n"
            "- Separa los títulos usando el símbolo `|` (barra vertical) **sin espacios extra**.\n"
            "- No expliques, no agregues comentarios, no completes con ejemplos adicionales, no inventes temas nuevos.\n"
            "- Solo responde los 3 títulos, unidos por `|`.\n\n"
            "**IMPORTANTE:**\n"
            "- Si no puedes identificar claramente 3 títulos válidos respetando las reglas anteriores, debes devolver exactamente la palabra: `NO_TITULOS`.\n"
            "- No improvises si no puedes cumplir las reglas.\n\n"
            "**Ejemplo de entrada:** 'Tengo una zapatería y quiero atraer más clientes.'\n"
            "**Ejemplo de salida correcta:** 'Zapatos en oferta|Compra fácil|Descuentos hoy'"
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
                    f"Le pediste que describiera su negocio y su objetivo, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"Este es el historial reciente de su conversación:\n\n"
                    f"{historial_texto}\n\n"
                    "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando por WhatsApp.\n\n"
                    "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                    "'Para ayudarte mejor, necesito que me cuentes brevemente a qué se dedica tu negocio y cuál es tu objetivo principal con estos anuncios. "
                    "Y si deseas salir del proceso, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                    "No repitas literal lo que dijo el usuario. No expliques que estás leyendo historial. Usa máximo 5 líneas, manteniendo un tono humano, cálido y de acompañamiento."
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
        update_user_field(numero_usuario, "Estado Anuncio", "Titulos Generados")

        print(f"[LOG] Títulos generados correctamente: {titulos_limpios} para número: {numero_usuario}")

        from src.services.FSM.titles.flujo_creacion_titulos import ejecutar_flujo_creacion_titulos
        return ejecutar_flujo_creacion_titulos(numero_usuario)

    except Exception:
        return "Hubo un problema al generar tus títulos. ¿Podrías describirme nuevamente tu negocio y objetivo, por favor?"

















from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_generacion_titulos(numero_usuario, mensaje_usuario):
    """
    Procesa la respuesta del usuario para generar 3 títulos publicitarios de máximo 30 caracteres.
    Si no se detectan bien, vuelve a pedir amablemente más información.
    """

    # Paso 1: Intentar generar los títulos
    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads especializado en crear títulos publicitarios breves, claros y atractivos para campañas en línea.\n"
            "El usuario te proporcionará una breve descripción de su negocio y su objetivo principal.\n\n"
            "**Tu tarea es OBLIGATORIAMENTE:**\n"
            "- Generar exactamente **3 títulos** basados en la información dada.\n"
            "- Cada título debe tener como máximo **30 caracteres**.\n"
            "- Si el contenido del usuario es muy extenso, debes **resumir o parafrasear creativamente** sin inventar información nueva.\n"
            "- Separa los títulos usando el símbolo `|` (barra vertical) **sin espacios extra**.\n"
            "- No expliques, no agregues comentarios, no completes con ejemplos adicionales, no inventes temas nuevos.\n"
            "- Solo responde los 3 títulos, unidos por `|`.\n\n"
            "**IMPORTANTE:**\n"
            "- Si no puedes identificar claramente 3 títulos válidos respetando las reglas anteriores, debes devolver exactamente la palabra: `NO_TITULOS`.\n"
            "- No improvises si no puedes cumplir las reglas.\n\n"
            "**Ejemplo de entrada:** 'Tengo una zapatería y quiero atraer más clientes.'\n"
            "**Ejemplo de salida correcta:** 'Zapatos en oferta|Compra fácil|Descuentos hoy'"
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
                    f"Le pediste que describiera su negocio y su objetivo, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"Este es el historial reciente de su conversación:\n\n"
                    f"{historial_texto}\n\n"
                    "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando por WhatsApp.\n\n"
                    "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                    "'Para ayudarte mejor, necesito que me cuentes brevemente a qué se dedica tu negocio y cuál es tu objetivo principal con estos anuncios. "
                    "Y si deseas salir del proceso, puedes escribir SALIR en mayúsculas y sin signos de puntuación.'\n\n"
                    "No repitas literal lo que dijo el usuario. No expliques que estás leyendo historial. Usa máximo 5 líneas, manteniendo un tono humano, cálido y de acompañamiento."
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
        update_user_field(numero_usuario, "Estado Anuncio", "Titulos Generados")

        print(f"[LOG] Títulos generados correctamente: {titulos_limpios} para número: {numero_usuario}")

        from src.services.FSM.flujo_creacion_anuncio import ejecutar_flujo_creacion_anuncio
        return ejecutar_flujo_creacion_anuncio(numero_usuario)

    except Exception:
        return "Hubo un problema al generar tus títulos. ¿Podrías describirme nuevamente tu negocio y objetivo, por favor?"


'''