from src.services.response_service import generar_respuesta
from src.services.intention_router import preparar_historial_con_inyeccion
from src.config import USAR_FIRESTORE
from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
from src.data.firestore_storage import guardar_mensaje
from src.data.chatbot_sheet_connector import get_user_field, update_user_field

if not USAR_FIRESTORE:
    from src.data.conversation_storage import guardar_en_historial


def get_response(text, numero_usuario):
    """
    Procesa el mensaje del usuario y genera una respuesta para WhatsApp.
    """

    texto = text.strip()

    # 🔴 SALIR del flujo de creación — solo si es exactamente "SALIR" en mayúsculas
    if texto == "SALIR":
        respuesta = "Saliste del proceso de creación de campaña. Puedes seguir preguntando lo que desees 😊"

        if USAR_FIRESTORE:
            guardar_mensaje(numero_usuario, "assistant", respuesta)

        estado_campana = get_user_field(numero_usuario, "Estado Campana")
        estado_anuncio = get_user_field(numero_usuario, "Estado Anuncio")

        # 🧼 Caso 1: El usuario salió antes de completar la campaña
        if estado_campana != "Campana Complete":
            campos_a_borrar = ["User Name", "Campaign Name", "Segmentation", "Requested Budget"]
            for campo in campos_a_borrar:
                update_user_field(numero_usuario, campo, "")

            # Restablecer estado si algún dato está incompleto
            falta_dato = any(get_user_field(numero_usuario, campo) in [None, ""] for campo in campos_a_borrar)
            if falta_dato:
                update_user_field(numero_usuario, "Estado Campana", "no iniciada")

        # 🧼 Caso 2: La campaña fue completada pero el anuncio aún no
        elif estado_anuncio != "Anuncio Completed":
            campos_a_borrar = ["Titles", "Descriptions", "Keywords"]
            for campo in campos_a_borrar:
                update_user_field(numero_usuario, campo, "")

            # Reiniciar flujo de anuncio si el usuario se detuvo a medio camino
            update_user_field(numero_usuario, "Estado Anuncio", "no iniciado")

        return respuesta

    # 🟢 INICIAR el flujo FSM — solo si es exactamente "CREAR CAMPAÑA"
    if texto == "CREAR CAMPAÑA":
        return ejecutar_flujo_creacion_campana(numero_usuario)

    # 🔁 FSM activo: ejecutar si el estado indica que el usuario está en medio del proceso
    estado_campana = get_user_field(numero_usuario, "Estado Campana")
    estado_anuncio = get_user_field(numero_usuario, "Estado Anuncio")
    if (
        (estado_campana not in [None, "", "no iniciada", "Campana Complete"])
        or (estado_anuncio not in [None, "", "no iniciado", "Anuncio Completed"])
    ):
        return ejecutar_flujo_creacion_campana(numero_usuario, texto)

    # ⚪️ Proceso normal: intenciones + GPT
    resultado = preparar_historial_con_inyeccion(texto, numero_usuario)

    if resultado.get("respuesta_directa"):
        respuesta = resultado["respuesta_directa"]

        if not USAR_FIRESTORE:
            guardar_en_historial(numero_usuario, {"role": "user", "content": text})
            guardar_en_historial(numero_usuario, {"role": "assistant", "content": respuesta})

        return respuesta

    return generar_respuesta(text, numero_usuario, resultado["historial"])









'''
from src.services.response_service import generar_respuesta
from src.services.intention_router import preparar_historial_con_inyeccion
from src.config import USAR_FIRESTORE
from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
from src.data.firestore_storage import guardar_mensaje
from src.data.chatbot_sheet_connector import get_user_field, update_user_field

if not USAR_FIRESTORE:
    from src.data.conversation_storage import guardar_en_historial


def get_response(text, numero_usuario):
    """
    Procesa el mensaje del usuario y genera una respuesta para WhatsApp.
    """

    texto = text.strip()

    # 🔴 SALIR del flujo de creación — solo si es exactamente "SALIR" en mayúsculas
    if texto == "SALIR":
        respuesta = "Saliste del proceso de creación de campaña. Puedes seguir preguntando lo que desees 😊"

        if USAR_FIRESTORE:
            guardar_mensaje(numero_usuario, "assistant", respuesta)

        # 🧼 Limpiar los datos del proceso en Google Sheets
        campos_a_borrar = ["User Name", "Campaign Name", "Segmentation", "Requested Budget"]
        for campo in campos_a_borrar:
            update_user_field(numero_usuario, campo, "")

        # 🔁 Restablecer estado si no todos los campos fueron llenados
        falta_dato = any(get_user_field(numero_usuario, campo) in [None, ""] for campo in campos_a_borrar)
        if falta_dato:
            update_user_field(numero_usuario, "Estado Campana", "no iniciada")

        return respuesta

    # 🟢 INICIAR el flujo FSM — solo si es exactamente "CREAR CAMPAÑA"
    if texto == "CREAR CAMPAÑA":
        return ejecutar_flujo_creacion_campana(numero_usuario)

    # 🔁 FSM activo: ejecutar si el estado indica que el usuario está en medio del proceso
    estado_campana = get_user_field(numero_usuario, "Estado Campana")
    estado_anuncio = get_user_field(numero_usuario, "Estado Anuncio")
    if (
        (estado_campana not in [None, "", "no iniciada", "Campana Complete"])
        or (estado_anuncio not in [None, "", "no iniciado", "Anuncio Completed"])
    ):
        return ejecutar_flujo_creacion_campana(numero_usuario, texto)

    # ⚪️ Proceso normal: intenciones + GPT
    resultado = preparar_historial_con_inyeccion(texto, numero_usuario)

    if resultado.get("respuesta_directa"):
        respuesta = resultado["respuesta_directa"]

        if not USAR_FIRESTORE:
            guardar_en_historial(numero_usuario, {"role": "user", "content": text})
            guardar_en_historial(numero_usuario, {"role": "assistant", "content": respuesta})

        return respuesta

    return generar_respuesta(text, numero_usuario, resultado["historial"])



















from src.services.response_service import generar_respuesta
from src.services.intention_router import preparar_historial_con_inyeccion
from src.config import USAR_FIRESTORE
from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
from src.data.firestore_storage import guardar_mensaje
from src.data.chatbot_sheet_connector import get_user_field, update_user_field

if not USAR_FIRESTORE:
    from src.data.conversation_storage import guardar_en_historial


def get_response(text, numero_usuario):
    """
    Procesa el mensaje del usuario y genera una respuesta para WhatsApp.
    """

    texto = text.strip()

    # 🔴 SALIR del flujo de creación — solo si es exactamente "SALIR" en mayúsculas
    if texto == "SALIR":
        respuesta = "Saliste del proceso de creación de campaña. Puedes seguir preguntando lo que desees 😊"

        if USAR_FIRESTORE:
            guardar_mensaje(numero_usuario, "assistant", respuesta)

        # 🧼 Limpiar los datos del proceso en Google Sheets
        campos_a_borrar = ["User Name", "Campaign Name", "Segmentation", "Requested Budget"]
        for campo in campos_a_borrar:
            update_user_field(numero_usuario, campo, "")

        # 🔁 Restablecer estado si no todos los campos fueron llenados
        falta_dato = any(get_user_field(numero_usuario, campo) in [None, ""] for campo in campos_a_borrar)
        if falta_dato:
            update_user_field(numero_usuario, "Estado Campana", "no iniciada")

        return respuesta

    # 🟢 INICIAR el flujo FSM — solo si es exactamente "CREAR CAMPAÑA"
    if texto == "CREAR CAMPAÑA":
        return ejecutar_flujo_creacion_campana(numero_usuario)

    # 🔁 FSM activo: ejecutar si el estado indica que el usuario está en medio del proceso
    estado_actual = get_user_field(numero_usuario, "Estado Campana")
    if estado_actual not in [None, "", "no iniciada", "Campana Complete"]:
        return ejecutar_flujo_creacion_campana(numero_usuario, texto)

    # ⚪️ Proceso normal: intenciones + GPT
    resultado = preparar_historial_con_inyeccion(texto, numero_usuario)

    if resultado.get("respuesta_directa"):
        respuesta = resultado["respuesta_directa"]

        if not USAR_FIRESTORE:
            guardar_en_historial(numero_usuario, {"role": "user", "content": text})
            guardar_en_historial(numero_usuario, {"role": "assistant", "content": respuesta})

        return respuesta

    return generar_respuesta(text, numero_usuario, resultado["historial"])












from src.services.response_service import generar_respuesta
from src.services.intention_router import preparar_historial_con_inyeccion
from src.config import USAR_FIRESTORE
from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
from src.data.firestore_storage import guardar_mensaje
from src.data.chatbot_sheet_connector import get_user_field, update_user_field

if not USAR_FIRESTORE:
    from src.data.conversation_storage import guardar_en_historial


def get_response(text, numero_usuario):
    """
    Procesa el mensaje del usuario y genera una respuesta para WhatsApp.
    """

    texto = text.strip()

    # 🔴 SALIR del flujo de creación — solo si es exactamente "SALIR" en mayúsculas
    if texto == "SALIR":
        respuesta = "Saliste del proceso de creación de campaña. Puedes seguir preguntando lo que desees 😊"

        if USAR_FIRESTORE:
            guardar_mensaje(numero_usuario, "assistant", respuesta)

        # 🔍 Verificamos si falta algún dato clave
        campos_necesarios = ["User Name", "Campaign Name", "Segmentation", "Requested Budget"]
        falta_dato = any(get_user_field(numero_usuario, campo) in [None, ""] for campo in campos_necesarios)

        if falta_dato:
            update_user_field(numero_usuario, "Estado Campana", "no iniciada")

        return respuesta

    # 🟢 INICIAR el flujo FSM — solo si es exactamente "CREAR CAMPAÑA"
    if texto == "CREAR CAMPAÑA":
        return ejecutar_flujo_creacion_campana(numero_usuario)

    # 🔁 FSM activo: ejecutar si el estado indica que el usuario está en medio del proceso
    estado_actual = get_user_field(numero_usuario, "Estado Campana")
    if estado_actual not in [None, "", "no iniciada", "Campana Complete"]:
        return ejecutar_flujo_creacion_campana(numero_usuario, texto)

    # ⚪️ Proceso normal: intenciones + GPT
    resultado = preparar_historial_con_inyeccion(texto, numero_usuario)

    if resultado.get("respuesta_directa"):
        respuesta = resultado["respuesta_directa"]

        if not USAR_FIRESTORE:
            guardar_en_historial(numero_usuario, {"role": "user", "content": text})
            guardar_en_historial(numero_usuario, {"role": "assistant", "content": respuesta})

        return respuesta

    return generar_respuesta(text, numero_usuario, resultado["historial"])













from src.services.response_service import generar_respuesta
from src.services.intention_router import preparar_historial_con_inyeccion
from src.config import USAR_FIRESTORE
from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
from src.data.firestore_storage import guardar_mensaje
from src.data.chatbot_sheet_connector import get_user_field

if not USAR_FIRESTORE:
    from src.data.conversation_storage import guardar_en_historial


def get_response(text, numero_usuario):
    """
    Procesa el mensaje del usuario y genera una respuesta para WhatsApp.
    """

    texto = text.strip()

    # 🔴 SALIR del flujo de creación — solo si es exactamente "SALIR" en mayúsculas
    if texto == "SALIR":
        respuesta = "Saliste del proceso de creación de campaña. Puedes seguir preguntando lo que desees 😊"
        if USAR_FIRESTORE:
            guardar_mensaje(numero_usuario, "assistant", respuesta)
        return respuesta

    # 🟢 INICIAR el flujo FSM — solo si es exactamente "CREAR CAMPAÑA"
    if texto == "CREAR CAMPAÑA":
        return ejecutar_flujo_creacion_campana(numero_usuario)

    # 🔁 FSM activo: ejecutar si el estado indica que el usuario está en medio del proceso
    estado_actual = get_user_field(numero_usuario, "Estado Campana")
    if estado_actual not in [None, "", "no iniciada", "Campana Complete"]:
        return ejecutar_flujo_creacion_campana(numero_usuario, texto)

    # ⚪️ Proceso normal: intenciones + GPT
    resultado = preparar_historial_con_inyeccion(texto, numero_usuario)

    if resultado.get("respuesta_directa"):
        respuesta = resultado["respuesta_directa"]

        if not USAR_FIRESTORE:
            guardar_en_historial(numero_usuario, {"role": "user", "content": text})
            guardar_en_historial(numero_usuario, {"role": "assistant", "content": respuesta})

        return respuesta

    return generar_respuesta(text, numero_usuario, resultado["historial"])






























from src.services.response_service import generar_respuesta
from src.services.intention_router import preparar_historial_con_inyeccion
from src.config import USAR_FIRESTORE

if not USAR_FIRESTORE:
    from src.data.conversation_storage import guardar_en_historial


def get_response(text, numero_usuario):
    """
    Procesa el mensaje del usuario y genera una respuesta para WhatsApp.
    """

    resultado = preparar_historial_con_inyeccion(text, numero_usuario)

    # Si se detectó una intención preprogramada (respuesta directa desde helper)
    if resultado.get("respuesta_directa"):
        respuesta = resultado["respuesta_directa"]

        # Solo se guarda en local
        if not USAR_FIRESTORE:
            guardar_en_historial(numero_usuario, {"role": "user", "content": text})
            guardar_en_historial(numero_usuario, {"role": "assistant", "content": respuesta})

        return respuesta

    # ✅ Ya no se añade manualmente el mensaje del usuario
    return generar_respuesta(text, numero_usuario, resultado["historial"])














from src.services.response_service import generar_respuesta
from src.services.intention_router import preparar_historial_con_inyeccion
from src.config import USAR_FIRESTORE

# Importamos la función para guardar historial solo si no se usa Firestore
if not USAR_FIRESTORE:
    from src.data.conversation_storage import guardar_en_historial


def get_response(text, numero_usuario):
    """
    Procesa el mensaje del usuario y genera una respuesta para WhatsApp.

    - Si se detecta una intención preprogramada (como 'quién te creó'), se responde de inmediato.
    - Si no hay intención, GPT responderá normalmente usando el historial.
    """

    resultado = preparar_historial_con_inyeccion(text, numero_usuario)

    # Si se detectó una intención preprogramada (respuesta directa desde helper)
    if resultado.get("respuesta_directa"):
        respuesta = resultado["respuesta_directa"]

        # Guardado del historial solo si se usa almacenamiento local
        if not USAR_FIRESTORE:
            guardar_en_historial(numero_usuario, {"role": "user", "content": text})
            guardar_en_historial(numero_usuario, {"role": "assistant", "content": respuesta})

        return respuesta

    # Si no hay intención, añadimos manualmente el mensaje del usuario al historial en memoria
    resultado["historial"].append({
        "role": "user",
        "content": text
    })

    return generar_respuesta(text, numero_usuario, resultado["historial"])



















from src.services.response_service import generar_respuesta
from src.services.intention_router import preparar_historial_con_inyeccion
from src.config import USAR_FIRESTORE

# Importamos la función para guardar historial solo si no se usa Firestore
if not USAR_FIRESTORE:
    from src.data.conversation_storage import guardar_en_historial


def get_response(text, numero_usuario):
    """
    Procesa el mensaje del usuario y genera una respuesta para WhatsApp.

    - Si se detecta una intención preprogramada (como 'quién te creó'), se responde de inmediato.
    - Si no hay intención, GPT responderá normalmente usando el historial.
    """

    resultado = preparar_historial_con_inyeccion(text, numero_usuario)

    # Si se detectó una intención preprogramada (respuesta directa desde helper)
    if resultado.get("respuesta_directa"):
        respuesta = resultado["respuesta_directa"]

        # Guardado del historial solo si se usa almacenamiento local
        if not USAR_FIRESTORE:
            guardar_en_historial(numero_usuario, {"role": "user", "content": text})
            guardar_en_historial(numero_usuario, {"role": "assistant", "content": respuesta})

        return respuesta

    # Si no hay intención, GPT responde con historial
    return generar_respuesta(text, numero_usuario, resultado["historial"])
'''
