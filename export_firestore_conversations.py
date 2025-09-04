import os
import json
from google.cloud import firestore

# Ruta al archivo de credenciales
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "CredentialsGoogleFirestore.json"

# Carpeta de destino para los archivos exportados
EXPORT_FOLDER = "firestore_exports"

# Crear carpeta si no existe
if not os.path.exists(EXPORT_FOLDER):
    os.makedirs(EXPORT_FOLDER)

# Inicializar cliente Firestore
db = firestore.Client()
coleccion = db.collection("conversations")  # CORREGIDO

print("Exportando documentos...")

# Leer y guardar cada documento
docs = coleccion.stream()
for doc in docs:
    data = doc.to_dict()
    file_name = os.path.join(EXPORT_FOLDER, f"{doc.id}.json")
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Exportado: {file_name}")

print("\n✅ Exportación completa. Archivos guardados en:", EXPORT_FOLDER)
