import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Ruta a las credenciales
RUTA_CREDENCIALES = os.path.join(os.path.dirname(__file__), "../../CredentialsGoogleFirestore.json")

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(RUTA_CREDENCIALES)
    firebase_admin.initialize_app(cred, {
        "projectId": "servidor-chatbot-448603"
    })

# Cliente Firestore
db = firestore.client()

# Configuración general
COLECCION_CONVERSACIONES = "conversations"
MAX_MENSAJES_USUARIO = 6
MAX_MENSAJES_BOT = 6

def guardar_mensaje(numero, role, mensaje):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    nuevo_mensaje = {
        "role": role,
        "content": mensaje,
        "timestamp": datetime.utcnow().isoformat()
    }

    if doc.exists:
        datos = doc.to_dict()
        historial = datos.get("historial", [])
        historial.append(nuevo_mensaje)
        doc_ref.update({
            "historial": historial,
            "ultima_actualizacion": nuevo_mensaje["timestamp"]
        })
    else:
        doc_ref.set({
            "nombre": "Usuario",
            "historial": [nuevo_mensaje],
            "ultima_actualizacion": nuevo_mensaje["timestamp"]
        })

def leer_historial(numero, max_user=MAX_MENSAJES_USUARIO, max_bot=MAX_MENSAJES_BOT):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if not doc.exists:
        return []

    datos = doc.to_dict()
    historial = datos.get("historial", [])

    ultimos_usuario = [
        m for m in reversed(historial)
        if isinstance(m, dict) and m.get("role") == "user"
    ][:max_user]

    ultimos_bot = [
        m for m in reversed(historial)
        if isinstance(m, dict) and m.get("role") == "assistant"
    ][:max_bot]

    combinados = sorted(ultimos_usuario + ultimos_bot, key=lambda x: x.get("timestamp", ""))
    return combinados

def actualizar_nombre(numero, nombre):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({
            "nombre": nombre,
            "ultima_actualizacion": datetime.utcnow().isoformat()
        })
    else:
        doc_ref.set({
            "nombre": nombre,
            "historial": [],
            "ultima_actualizacion": datetime.utcnow().isoformat()
        })

def obtener_nombre(numero):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    datos = doc.to_dict()
    nombre = datos.get("nombre", "")
    return nombre if nombre.lower() != "usuario" else None

# 🟩 Control de procesamiento duplicado

COLECCION_MENSAJES_PROCESADOS = "mensajes_procesados"

def ya_procesado(message_id):
    return db.collection(COLECCION_MENSAJES_PROCESADOS).document(message_id).get().exists

def registrar_id_procesado(message_id, numero):
    """
    Intenta registrar un ID de mensaje. Devuelve False si ya estaba registrado.
    """
    doc_ref = db.collection(COLECCION_MENSAJES_PROCESADOS).document(message_id)
    if doc_ref.get().exists:
        return False  # Ya estaba registrado

    doc_ref.set({
        "numero": numero,
        "timestamp": datetime.utcnow().isoformat()
    })
    return True



'''
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Ruta a las credenciales
RUTA_CREDENCIALES = os.path.join(os.path.dirname(__file__), "../../CredentialsGoogleFirestore.json")

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(RUTA_CREDENCIALES)
    firebase_admin.initialize_app(cred, {
        "projectId": "servidor-chatbot-448603"
    })

# Cliente Firestore
db = firestore.client()

# Configuración general
COLECCION_CONVERSACIONES = "conversations"
MAX_MENSAJES_USUARIO = 6
MAX_MENSAJES_BOT = 6


def guardar_mensaje(numero, role, mensaje):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    nuevo_mensaje = {
        "role": role,
        "content": mensaje,
        "timestamp": datetime.utcnow().isoformat()
    }

    if doc.exists:
        datos = doc.to_dict()
        historial = datos.get("historial", [])
        historial.append(nuevo_mensaje)
        doc_ref.update({
            "historial": historial,
            "ultima_actualizacion": nuevo_mensaje["timestamp"]
        })
    else:
        doc_ref.set({
            "nombre": "Usuario",
            "historial": [nuevo_mensaje],
            "ultima_actualizacion": nuevo_mensaje["timestamp"]
        })


def leer_historial(numero, max_user=MAX_MENSAJES_USUARIO, max_bot=MAX_MENSAJES_BOT):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if not doc.exists:
        return []

    datos = doc.to_dict()
    historial = datos.get("historial", [])

    ultimos_usuario = [
        m for m in reversed(historial)
        if isinstance(m, dict) and m.get("role") == "user"
    ][:max_user]

    ultimos_bot = [
        m for m in reversed(historial)
        if isinstance(m, dict) and m.get("role") == "assistant"
    ][:max_bot]

    combinados = sorted(ultimos_usuario + ultimos_bot, key=lambda x: x.get("timestamp", ""))
    return combinados


def actualizar_nombre(numero, nombre):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({
            "nombre": nombre,
            "ultima_actualizacion": datetime.utcnow().isoformat()
        })
    else:
        doc_ref.set({
            "nombre": nombre,
            "historial": [],
            "ultima_actualizacion": datetime.utcnow().isoformat()
        })


def obtener_nombre(numero):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    datos = doc.to_dict()
    nombre = datos.get("nombre", "")
    return nombre if nombre.lower() != "usuario" else None


# NUEVO: Control de procesamiento duplicado por message_id

COLECCION_MENSAJES_PROCESADOS = "mensajes_procesados"

def ya_procesado(message_id):
    return db.collection(COLECCION_MENSAJES_PROCESADOS).document(message_id).get().exists

def registrar_id_procesado(message_id, numero):
    db.collection(COLECCION_MENSAJES_PROCESADOS).document(message_id).set({
        "numero": numero,
        "timestamp": datetime.utcnow().isoformat()
    })

























import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Ruta a las credenciales
RUTA_CREDENCIALES = os.path.join(os.path.dirname(__file__), "../../CredentialsGoogleFirestore.json")

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(RUTA_CREDENCIALES)
    firebase_admin.initialize_app(cred, {
        "projectId": "servidor-chatbot-448603"
    })

# Cliente Firestore
db = firestore.client()

# Configuración general
COLECCION_CONVERSACIONES = "conversations"
MAX_MENSAJES_USUARIO = 6
MAX_MENSAJES_BOT = 6

def guardar_mensaje(numero, role, mensaje):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    nuevo_mensaje = {
        "role": role,
        "content": mensaje,
        "timestamp": datetime.utcnow().isoformat()
    }

    if doc.exists:
        datos = doc.to_dict()
        historial = datos.get("historial", [])
        historial.append(nuevo_mensaje)
        doc_ref.update({
            "historial": historial,
            "ultima_actualizacion": nuevo_mensaje["timestamp"]
        })
    else:
        doc_ref.set({
            "nombre": "Usuario",
            "historial": [nuevo_mensaje],
            "ultima_actualizacion": nuevo_mensaje["timestamp"]
        })

def leer_historial(numero, max_user=MAX_MENSAJES_USUARIO, max_bot=MAX_MENSAJES_BOT):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if not doc.exists:
        return []

    datos = doc.to_dict()
    historial = datos.get("historial", [])

    # ✅ Filtrar correctamente y prevenir errores por mensajes corruptos
    ultimos_usuario = [
        m for m in reversed(historial)
        if isinstance(m, dict) and m.get("role") == "user"
    ][:max_user]

    ultimos_bot = [
        m for m in reversed(historial)
        if isinstance(m, dict) and m.get("role") == "assistant"
    ][:max_bot]

    combinados = sorted(ultimos_usuario + ultimos_bot, key=lambda x: x.get("timestamp", ""))
    return combinados

def actualizar_nombre(numero, nombre):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({
            "nombre": nombre,
            "ultima_actualizacion": datetime.utcnow().isoformat()
        })
    else:
        doc_ref.set({
            "nombre": nombre,
            "historial": [],
            "ultima_actualizacion": datetime.utcnow().isoformat()
        })

def obtener_nombre(numero):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    datos = doc.to_dict()
    nombre = datos.get("nombre", "")
    return nombre if nombre.lower() != "usuario" else None
















ERROR ROLE PILLADO CON TRACEBACK

import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Ruta a las credenciales
RUTA_CREDENCIALES = os.path.join(os.path.dirname(__file__), "../../CredentialsGoogleFirestore.json")

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(RUTA_CREDENCIALES)
    firebase_admin.initialize_app(cred, {
        "projectId": "servidor-chatbot-448603"
    })

# Cliente Firestore
db = firestore.client()

# Configuración general
COLECCION_CONVERSACIONES = "conversations"
MAX_MENSAJES_USUARIO = 6
MAX_MENSAJES_BOT = 6

def guardar_mensaje(numero, role, mensaje):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    nuevo_mensaje = {
        "role": role,
        "content": mensaje,
        "timestamp": datetime.utcnow().isoformat()
    }

    if doc.exists:
        datos = doc.to_dict()
        historial = datos.get("historial", [])
        historial.append(nuevo_mensaje)
        doc_ref.update({
            "historial": historial,
            "ultima_actualizacion": nuevo_mensaje["timestamp"]
        })
    else:
        doc_ref.set({
            "nombre": "Usuario",
            "historial": [nuevo_mensaje],
            "ultima_actualizacion": nuevo_mensaje["timestamp"]
        })

def leer_historial(numero, max_user=MAX_MENSAJES_USUARIO, max_bot=MAX_MENSAJES_BOT):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if not doc.exists:
        return []

    datos = doc.to_dict()
    historial = datos.get("historial", [])
    ultimos_usuario = [m for m in reversed(historial) if m["role"] == "user"][:max_user]
    ultimos_bot = [m for m in reversed(historial) if m["role"] == "assistant"][:max_bot]
    combinados = sorted(ultimos_usuario + ultimos_bot, key=lambda x: x["timestamp"])
    return combinados

def actualizar_nombre(numero, nombre):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({
            "nombre": nombre,
            "ultima_actualizacion": datetime.utcnow().isoformat()
        })
    else:
        doc_ref.set({
            "nombre": nombre,
            "historial": [],
            "ultima_actualizacion": datetime.utcnow().isoformat()
        })

def obtener_nombre(numero):
    doc_ref = db.collection(COLECCION_CONVERSACIONES).document(numero)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    datos = doc.to_dict()
    nombre = datos.get("nombre", "")
    return nombre if nombre.lower() != "usuario" else None

'''