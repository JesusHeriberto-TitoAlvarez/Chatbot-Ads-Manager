from datetime import datetime
import json
import os

# Carpeta interna: src/data/conversations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_CONVERSACIONES = os.path.join(BASE_DIR, "conversations")

# Configuración flexible
MAX_MENSAJES_USUARIO = 6
MAX_MENSAJES_BOT = 6

# Crear carpeta si no existe
if not os.path.exists(CARPETA_CONVERSACIONES):
    os.makedirs(CARPETA_CONVERSACIONES)

def ruta_archivo(numero):
    return os.path.join(CARPETA_CONVERSACIONES, f"{numero}.json")

def inicializar_conversacion(numero):
    ruta = ruta_archivo(numero)
    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump({
                "nombre": "Usuario",
                "historial": [],
                "ultima_actualizacion": datetime.utcnow().isoformat()
            }, f, indent=2)

def agregar_mensaje(numero, role, mensaje):
    inicializar_conversacion(numero)
    ruta = ruta_archivo(numero)
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    nuevo_mensaje = {
        "role": role,
        "content": mensaje,
        "timestamp": datetime.utcnow().isoformat()
    }

    datos["historial"].append(nuevo_mensaje)
    datos["ultima_actualizacion"] = nuevo_mensaje["timestamp"]

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2)

def leer_historial(numero, max_user=MAX_MENSAJES_USUARIO, max_bot=MAX_MENSAJES_BOT):
    ruta = ruta_archivo(numero)
    if not os.path.exists(ruta):
        return []

    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    historial = datos.get("historial", [])
    ultimos_usuario = [m for m in reversed(historial) if m["role"] == "user"][:max_user]
    ultimos_bot = [m for m in reversed(historial) if m["role"] == "assistant"][:max_bot]
    
    mensajes_combinados = sorted(ultimos_usuario + ultimos_bot, key=lambda x: x["timestamp"])
    return mensajes_combinados

def actualizar_nombre(numero, nombre):
    ruta = ruta_archivo(numero)
    if not os.path.exists(ruta):
        inicializar_conversacion(numero)

    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    datos["nombre"] = nombre
    datos["ultima_actualizacion"] = datetime.utcnow().isoformat()

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2)

def obtener_nombre(numero):
    ruta = ruta_archivo(numero)
    if not os.path.exists(ruta):
        return None

    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    nombre = datos.get("nombre", "")
    return nombre if nombre.lower() != "usuario" else None
