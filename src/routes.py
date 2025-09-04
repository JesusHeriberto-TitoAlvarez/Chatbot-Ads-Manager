from flask import Blueprint, request, jsonify
from src.config import VERIFY_TOKEN, USAR_FIRESTORE
from src.chatbot import get_response
from src.services.message_service import send_message
from src.data.firestore_storage import (
    guardar_mensaje as agregar_mensaje,
    leer_historial,
    registrar_id_procesado  # 👈 usamos directamente esto ahora
)
from src.data.chatbot_sheet_connector import create_user_if_not_exists
import traceback

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return str(challenge), 200
        return "Token inválido", 403

    if request.method == "POST":
        try:
            data = request.get_json()
            if not data or "entry" not in data:
                return jsonify({"error": "Datos de entrada no válidos"}), 400

            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        message = change["value"]["messages"][0]
                        sender_id = message.get("from")
                        message_text = message.get("text", {}).get("body")
                        message_id = message.get("id")

                        if sender_id and message_text and message_id:
                            # 🔒 INTENTO DE REGISTRAR DIRECTAMENTE EL ID
                            if not registrar_id_procesado(message_id, sender_id):
                                print(f"[IGNORADO] Ya procesado (registro duplicado): {message_id}")
                                return "Ya procesado", 200

                            historial = leer_historial(sender_id)

                            if not historial:
                                agregar_mensaje(sender_id, "user", message_text)

                                # REGISTRO AUTOMÁTICO DEL NÚMERO EN GOOGLE SHEETS
                                create_user_if_not_exists(sender_id)

                                mensaje_bienvenida = (
                                    "*Bienvenido a Chatbot Ads Manager.*\n\n"
                                    "Estoy aquí para ayudarte a comprender cómo funciona la publicidad en Google y cómo hacer que tu negocio llegue a más personas por internet.\n\n"
                                    "También puedo *crear y publicar tus primeros anuncios reales de forma gratuita*. Solo tienes que pedírmelo cuando estés listo.\n\n"
                                    "Si quieres, puedes empezar preguntándome: ¿Qué es Google Ads?"
                                )

                                send_message(sender_id, mensaje_bienvenida)
                                return "Bienvenida enviada", 200

                            # Flujo normal desde el segundo mensaje
                            agregar_mensaje(sender_id, "user", message_text)
                            respuesta = get_response(message_text, sender_id)
                            send_message(sender_id, respuesta)

            return "Evento recibido", 200

        except Exception as e:
            print("======= TRACEBACK COMPLETO =======")
            traceback.print_exc()
            print("==================================")
            print(f"Error en webhook: {str(e)}")
            return jsonify({"error": str(e)}), 500




'''
from flask import Blueprint, request, jsonify
from src.config import VERIFY_TOKEN, USAR_FIRESTORE
from src.chatbot import get_response
from src.services.message_service import send_message
from src.data.firestore_storage import (
    guardar_mensaje as agregar_mensaje,
    leer_historial,
    ya_procesado,
    registrar_id_procesado
)
from src.data.chatbot_sheet_connector import create_user_if_not_exists  # IMPORTACIÓN NUEVA
import traceback

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return str(challenge), 200
        return "Token inválido", 403

    if request.method == "POST":
        try:
            data = request.get_json()
            if not data or "entry" not in data:
                return jsonify({"error": "Datos de entrada no válidos"}), 400

            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        message = change["value"]["messages"][0]
                        sender_id = message.get("from")
                        message_text = message.get("text", {}).get("body")
                        message_id = message.get("id")

                        if sender_id and message_text and message_id:
                            if ya_procesado(message_id):
                                print(f"[IGNORADO] Ya procesado: {message_id}")
                                return "Ya procesado", 200

                            registrar_id_procesado(message_id, sender_id)

                            historial = leer_historial(sender_id)

                            if not historial:
                                agregar_mensaje(sender_id, "user", message_text)

                                # REGISTRO AUTOMÁTICO DEL NÚMERO EN GOOGLE SHEETS
                                create_user_if_not_exists(sender_id)

                                mensaje_prueba = (
                                    "*¡Hola! 👋 Esta es una versión de prueba de Chatbot Ads Manager.*\n\n"
                                    "Estoy diseñado para ayudarte a entender y usar la publicidad digital, "
                                    "especialmente en la plataforma Google Ads.\n\n"
                                    "Si encuentras algún error o tienes sugerencias para mejorar, puedes escribirme directamente por este mismo chat. "
                                    "Tu opinión es muy valiosa para seguir mejorando la experiencia. ¡Gracias por confiar en mí! 🙌"
                                )
                                send_message(sender_id, mensaje_prueba)
                                return "Bienvenida enviada", 200

                            # Flujo normal desde el segundo mensaje
                            agregar_mensaje(sender_id, "user", message_text)
                            respuesta = get_response(message_text, sender_id)
                            send_message(sender_id, respuesta)

            return "Evento recibido", 200

        except Exception as e:
            print("======= TRACEBACK COMPLETO =======")
            traceback.print_exc()
            print("==================================")
            print(f"Error en webhook: {str(e)}")
            return jsonify({"error": str(e)}), 500





















from flask import Blueprint, request, jsonify
from src.config import VERIFY_TOKEN, USAR_FIRESTORE
from src.chatbot import get_response
from src.services.message_service import send_message
from src.data.firestore_storage import (
    guardar_mensaje as agregar_mensaje,
    leer_historial,
    ya_procesado,
    registrar_id_procesado
)
import traceback

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return str(challenge), 200
        return "Token inválido", 403

    if request.method == "POST":
        try:
            data = request.get_json()
            if not data or "entry" not in data:
                return jsonify({"error": "Datos de entrada no válidos"}), 400

            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        message = change["value"]["messages"][0]
                        sender_id = message.get("from")
                        message_text = message.get("text", {}).get("body")
                        message_id = message.get("id")  # Capturar ID único del mensaje

                        if sender_id and message_text and message_id:
                            # 🔒 Verificación de duplicados
                            if ya_procesado(message_id):
                                print(f"[IGNORADO] Ya procesado: {message_id}")
                                return "Ya procesado", 200

                            registrar_id_procesado(message_id, sender_id)

                            historial = leer_historial(sender_id)

                            if not historial:
                                agregar_mensaje(sender_id, "user", message_text)

                                mensaje_prueba = (
                                    "*¡Hola! 👋 Esta es una versión de prueba de Chatbot Ads Manager.*\n\n"
                                    "Estoy diseñado para ayudarte a entender y usar la publicidad digital, "
                                    "especialmente en la plataforma Google Ads.\n\n"
                                    "Si encuentras algún error o tienes sugerencias para mejorar, puedes escribirme directamente por este mismo chat. "
                                    "Tu opinión es muy valiosa para seguir mejorando la experiencia. ¡Gracias por confiar en mí! 🙌"
                                )
                                send_message(sender_id, mensaje_prueba)
                                return "Bienvenida enviada", 200

                            # Flujo normal desde el segundo mensaje
                            agregar_mensaje(sender_id, "user", message_text)
                            respuesta = get_response(message_text, sender_id)

                            # 🔁 Ya no se guarda manualmente el mensaje del bot
                            send_message(sender_id, respuesta)

            return "Evento recibido", 200

        except Exception as e:
            print("======= TRACEBACK COMPLETO =======")
            traceback.print_exc()
            print("==================================")
            print(f"Error en webhook: {str(e)}")
            return













from flask import Blueprint, request, jsonify
from src.config import VERIFY_TOKEN, USAR_FIRESTORE
from src.chatbot import get_response
from src.services.message_service import send_message
from src.data.firestore_storage import (
    guardar_mensaje as agregar_mensaje,
    leer_historial,
    ya_procesado,
    registrar_id_procesado
)
import traceback

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return str(challenge), 200
        return "Token inválido", 403

    if request.method == "POST":
        try:
            data = request.get_json()
            if not data or "entry" not in data:
                return jsonify({"error": "Datos de entrada no válidos"}), 400

            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        message = change["value"]["messages"][0]
                        sender_id = message.get("from")
                        message_text = message.get("text", {}).get("body")
                        message_id = message.get("id")  # Capturar ID único del mensaje

                        if sender_id and message_text and message_id:
                            # 🔒 Verificación de duplicados
                            if ya_procesado(message_id):
                                print(f"[IGNORADO] Ya procesado: {message_id}")
                                return "Ya procesado", 200

                            registrar_id_procesado(message_id, sender_id)

                            historial = leer_historial(sender_id)

                            if not historial:
                                agregar_mensaje(sender_id, "user", message_text)

                                mensaje_prueba = (
                                    "*¡Hola! 👋 Esta es una versión de prueba de Chatbot Ads Manager.*\n\n"
                                    "Estoy diseñado para ayudarte a entender y usar la publicidad digital, "
                                    "especialmente en la plataforma Google Ads.\n\n"
                                    "Si encuentras algún error o tienes sugerencias para mejorar, puedes escribirme directamente por este mismo chat. "
                                    "Tu opinión es muy valiosa para seguir mejorando la experiencia. ¡Gracias por confiar en mí! 🙌"
                                )
                                send_message(sender_id, mensaje_prueba)
                                return "Bienvenida enviada", 200

                            # Flujo normal desde el segundo mensaje
                            agregar_mensaje(sender_id, "user", message_text)
                            respuesta = get_response(message_text, sender_id)
                            agregar_mensaje(sender_id, "assistant", respuesta)  # ✅ Guardar antes de enviar
                            send_message(sender_id, respuesta)

            return "Evento recibido", 200

        except Exception as e:
            print("======= TRACEBACK COMPLETO =======")
            traceback.print_exc()
            print("==================================")
            print(f"Error en webhook: {str(e)}")
            return jsonify({"error": str(e)}), 500













from flask import Blueprint, request, jsonify
from src.config import VERIFY_TOKEN, USAR_FIRESTORE
from src.chatbot import get_response
from src.services.message_service import send_message
from src.data.firestore_storage import (
    guardar_mensaje as agregar_mensaje,
    leer_historial,
    ya_procesado,
    registrar_id_procesado
)
import traceback

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return str(challenge), 200
        return "Token inválido", 403

    if request.method == "POST":
        try:
            data = request.get_json()
            if not data or "entry" not in data:
                return jsonify({"error": "Datos de entrada no válidos"}), 400

            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        message = change["value"]["messages"][0]
                        sender_id = message.get("from")
                        message_text = message.get("text", {}).get("body")
                        message_id = message.get("id")  # Capturar ID único del mensaje

                        if sender_id and message_text and message_id:
                            # 🔒 Verificación de duplicados
                            if ya_procesado(message_id):
                                print(f"[IGNORADO] Ya procesado: {message_id}")
                                return "Ya procesado", 200

                            registrar_id_procesado(message_id, sender_id)

                            historial = leer_historial(sender_id)

                            if not historial:
                                agregar_mensaje(sender_id, "user", message_text)

                                mensaje_prueba = (
                                    "*¡Hola! 👋 Esta es una versión de prueba de Chatbot Ads Manager.*\n\n"
                                    "Estoy diseñado para ayudarte a entender y usar la publicidad digital, "
                                    "especialmente en la plataforma Google Ads.\n\n"
                                    "Si encuentras algún error o tienes sugerencias para mejorar, puedes escribirme directamente por este mismo chat. "
                                    "Tu opinión es muy valiosa para seguir mejorando la experiencia. ¡Gracias por confiar en mí! 🙌"
                                )
                                send_message(sender_id, mensaje_prueba)
                                return "Bienvenida enviada", 200

                            # Flujo normal desde el segundo mensaje
                            agregar_mensaje(sender_id, "user", message_text)
                            respuesta = get_response(message_text, sender_id)
                            send_message(sender_id, respuesta)

            return "Evento recibido", 200

        except Exception as e:
            print("======= TRACEBACK COMPLETO =======")
            traceback.print_exc()
            print("==================================")
            print(f"Error en webhook: {str(e)}")
            return jsonify({"error": str(e)}), 500






from flask import Blueprint, request, jsonify
from src.config import VERIFY_TOKEN, USAR_FIRESTORE
from src.chatbot import get_response
from src.services.message_service import send_message
from src.data.firestore_storage import guardar_mensaje as agregar_mensaje, leer_historial
import traceback  # AÑADIDO

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == VERIFY_TOKEN:
            return str(challenge), 200
        return "Token inválido", 403

    if request.method == "POST":
        try:
            data = request.get_json()
            if not data or "entry" not in data:
                return jsonify({"error": "Datos de entrada no válidos"}), 400

            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "messages" in change.get("value", {}):
                        message = change["value"]["messages"][0]
                        sender_id = message.get("from")
                        message_text = message.get("text", {}).get("body")

                        if sender_id and message_text:
                            historial = leer_historial(sender_id)

                            if not historial:
                                # Guardar el primer mensaje del usuario
                                agregar_mensaje(sender_id, "user", message_text)

                                # Enviar bienvenida (solo se guarda una vez automáticamente)
                                mensaje_prueba = (
                                    "*¡Hola! 👋 Esta es una versión de prueba de Chatbot Ads Manager.*\n\n"
                                    "Estoy diseñado para ayudarte a entender y usar la publicidad digital, "
                                    "especialmente en la plataforma Google Ads.\n\n"
                                    "Si encuentras algún error o tienes sugerencias para mejorar, puedes escribirme directamente por este mismo chat. "
                                    "Tu opinión es muy valiosa para seguir mejorando la experiencia. ¡Gracias por confiar en mí! 🙌"
                                )
                                send_message(sender_id, mensaje_prueba)

                                # NO responder con GPT aún
                                return "Bienvenida enviada", 200

                            # Flujo normal desde el segundo mensaje
                            agregar_mensaje(sender_id, "user", message_text)
                            respuesta = get_response(message_text, sender_id)
                            send_message(sender_id, respuesta)

            return "Evento recibido", 200

        except Exception as e:
            print("======= TRACEBACK COMPLETO =======")
            traceback.print_exc()  # Este imprimirá el error real con archivo y línea
            print("==================================")
            print(f"Error en webhook: {str(e)}")
            return jsonify({"error": str(e)}), 500


'''