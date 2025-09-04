from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_descripciones_usuario(numero_usuario, mensaje_usuario):
    """
    Procesa la respuesta del usuario para extraer 3 descripciones separadas por '|' y registrarlas.
    Si no se detectan bien, vuelve a pedirlas amablemente.
    """

    # Paso 1: Intentar extraer las descripciones
    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a los usuarios de WhatsApp a crear sus anuncios publicitarios.\n\n"
            "El usuario enviará un mensaje con 3 descripciones separadas por guiones (-).\n\n"
            "**Tu tarea es OBLIGATORIAMENTE:**\n"
            "- Extraer exactamente **3 descripciones publicitarias**.\n"
            "- Cada descripción debe tener como máximo **90 caracteres**.\n"
            "- Si una descripción supera los 90 caracteres, debes **resumir o parafrasear ligeramente** sin inventar contenido nuevo.\n"
            "- Devuelve las descripciones separadas estrictamente por el símbolo `|` (sin espacios antes ni después del `|`).\n\n"
            "**Ejemplo de entrada del usuario:**\n"
            "Estas son: Ofrecemos muebles de alta calidad para el hogar - Entrega rápida y segura - Diseño moderno y elegante.\n\n"
            "**Ejemplo de salida correcta:**\n"
            "'Muebles de alta calidad|Entrega rápida y segura|Diseño moderno y elegante'\n\n"
            "**Reglas estrictas:**\n"
            "- No agregues nuevas descripciones.\n"
            "- No inventes negocios diferentes.\n"
            "- No expliques tu respuesta ni escribas mensajes adicionales.\n"
            "- Si no puedes cumplir exactamente con las instrucciones, responde únicamente con `NO_DESCRIPCIONES` (en mayúsculas)."
        )},
        {"role": "user", "content": mensaje_usuario}
    ]

    try:
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=prompt,
            temperature=TEMPERATURA_DATOS_PERSONALES,
            max_tokens=150
        )

        descripciones_crudas = respuesta.choices[0].message.content.strip()

        if descripciones_crudas.count("|") != 2:
            descripciones_limpias = "NO_DESCRIPCIONES"
        else:
            descripciones_list = [d.strip() for d in descripciones_crudas.split("|") if d.strip()]
            if any(len(d) > 90 for d in descripciones_list):
                descripciones_limpias = "NO_DESCRIPCIONES"
            else:
                descripciones_limpias = descripciones_crudas

        # Paso 2: Validar resultados
        if descripciones_limpias == "NO_DESCRIPCIONES":
            # No se detectaron bien las descripciones
            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear su anuncio.\n"
                    f"Le pediste que te envíe 3 descripciones separadas por guiones, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de su conversación:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando normalmente por WhatsApp.\n\n"
                    "OBLIGATORIAMENTE debes PARAFRASEAR la siguiente idea dentro del mensaje:\n"
                    "'Necesito que me envíes 3 descripciones publicitarias separadas por guiones, como en este ejemplo: Muebles de calidad - Entrega rápida - Diseño elegante. "
                    "Si deseas, también puedes escribir *CREAR DESCRIPCIONES* en mayúsculas y yo te ayudaré a generarlas automáticamente para ti. "
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

            '''
            mensaje_reintento = respuesta_reintento.choices[0].message.content.strip()
            guardar_mensaje(numero_usuario, "assistant", mensaje_reintento)
            return mensaje_reintento
            '''

            mensaje_reintento = respuesta_reintento.choices[0].message.content.strip()
            mensaje_verificado = mensaje_reintento.lower()

            # ✅ Verificación obligatoria
            if "crear descripciones" not in mensaje_verificado or "salir" not in mensaje_verificado:
                mensaje_reintento = (
                    "Para continuar necesito que me envíes 3 descripciones publicitarias separadas por guiones, como: "
                    "Muebles de calidad - Entrega rápida - Diseño elegante. "
                    "También puedes escribir *CREAR DESCRIPCIONES* en mayúsculas para ayudarte automáticamente. "
                    "Y si deseas salir del proceso, escribe *SALIR* en mayúsculas."
                )

            guardar_mensaje(numero_usuario, "assistant", mensaje_reintento)
            return mensaje_reintento
            
        # ✅ Descripciones válidas
        update_user_field(numero_usuario, "Descriptions", descripciones_limpias)
        update_user_field(numero_usuario, "Estado Anuncio", "Descripciones Registradas")

        print(f"[LOG] Descripciones extraídas correctamente: {descripciones_limpias} para número: {numero_usuario}")

        # Import dinámico para evitar import circular
        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar tus descripciones. ¿Podrías enviarlas nuevamente separadas por guiones, por favor?"
