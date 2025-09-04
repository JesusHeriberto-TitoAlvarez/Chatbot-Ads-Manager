import requests
from src.config import ACCESS_TOKEN, PHONE_NUMBER_ID, USAR_FIRESTORE

# Cargar el módulo adecuado según el flag
if USAR_FIRESTORE:
    from src.data.firestore_storage import guardar_mensaje as agregar_mensaje
else:
    from src.data.conversation_storage import agregar_mensaje

def send_message(recipient_id, text):
    """Envía un mensaje a través de la API de WhatsApp y lo guarda en el historial."""
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(url, headers=headers, json=payload)

    # Guardar mensaje del chatbot en historial (Firestore o JSON)
    agregar_mensaje(recipient_id, "assistant", text)

    if response.status_code != 200:
        print(f"Error al enviar el mensaje: {response.text}")
    else:
        print("Mensaje enviado correctamente.")
