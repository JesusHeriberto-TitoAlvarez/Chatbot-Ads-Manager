import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno desde .env
load_dotenv()

# Token para verificación con WhatsApp API
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# API KEY de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Cliente OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# === Parámetros para controlar el comportamiento del modelo GPT ===

# Modelos por tipo de tarea
GPT_MODEL_GENERAL = "gpt-3.5-turbo"             # Conversaciones generales
GPT_MODEL_PRECISO = "gpt-3.5-turbo-1106"        # Para tareas críticas (nombre, ciudad, intención)
GPT_MODEL_AVANZADO = "gpt-4-0125-preview"       # Creatividad, razonamiento complejo

# Temperaturas específicas por tipo de tarea
TEMPERATURA_GPT = 0.7                           # General (heredado)
TEMPERATURA_CONVERSACION = 0.7                  # Para respuestas amables, naturales
TEMPERATURA_DATOS_PERSONALES = 0.3              # Para extraer nombres, ciudades, categorías
TEMPERATURA_INTENCIONES = 0.2                   # Para clasificar lo que el usuario quiere

# Por compatibilidad con código actual
GPT_MODEL = GPT_MODEL_GENERAL

# === CONTROL DEL TIPO DE ALMACENAMIENTO ===
# True = usa Firestore (en la nube)
# False = usa JSON local (en carpeta /data/conversations)
USAR_FIRESTORE = True

# USAR_FIRESTORE = True
# USAR_FIRESTORE = False
