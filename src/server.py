from flask import Flask
from src.routes import webhook_bp

app = Flask(__name__)

@app.route("/")
def home():
    return "Chatbot Ads Manager está en línea y listo para recibir mensajes por WhatsApp."

# Ruta especial para evitar errores 404/500 de App Engine
@app.route("/_ah/stop")
def stop_handler():
    return "OK", 200

# Registrar rutas del webhook
app.register_blueprint(webhook_bp)

# Bloque para ejecución local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)



'''
from flask import Flask
from src.routes import webhook_bp

app = Flask(__name__)

@app.route("/")
def home():
    return "El chatbot está funcionando correctamente."

app.register_blueprint(webhook_bp)

#Este bloque es para ejecución local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
'''