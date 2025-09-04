from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_DATOS_PERSONALES, TEMPERATURA_CONVERSACION
from src.data.chatbot_sheet_connector import update_user_field
from src.data.firestore_storage import guardar_mensaje, leer_historial
import re

def procesar_keywords_usuario(numero_usuario, mensaje_usuario):
    """
    Procesa la respuesta del usuario para extraer 3 palabras clave separadas por '|'.
    Si no se detectan bien, vuelve a pedirlas amablemente.
    """

    # Paso 1: Intentar extraer las keywords
    prompt = [
        {"role": "system", "content": (
            "Eres un chatbot profesional conectado con Google Ads para ayudar a los usuarios de WhatsApp a crear sus anuncios publicitarios.\n\n"
            "El usuario enviará un mensaje con 3 palabras clave separadas por guiones (-).\n\n"
            "**Tu tarea es OBLIGATORIAMENTE:**\n"
            "- Extraer exactamente **3 palabras clave**.\n"
            "- Cada palabra o frase clave debe tener como máximo **25 caracteres**.\n"
            "- Si alguna supera los 25 caracteres, debes **resumir o parafrasear ligeramente** sin inventar contenido nuevo.\n"
            "- Devuelve las keywords separadas estrictamente por el símbolo `|` (sin espacios antes ni después del `|`).\n\n"
            "**Ejemplo de entrada del usuario:**\n"
            "'comprar muebles baratos - oferta camas - colchones ortopédicos en descuento'\n\n"
            "**Ejemplo de salida correcta:**\n"
            "'comprar muebles|oferta camas|colchones ortopédicos'\n\n"
            "**Reglas estrictas:**\n"
            "- No agregues nuevas palabras clave.\n"
            "- No inventes productos o servicios diferentes.\n"
            "- No expliques tu respuesta ni escribas mensajes adicionales.\n"
            "- Si no puedes cumplir exactamente con las instrucciones, responde únicamente con `NO_KEYWORDS` (en mayúsculas)."
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

        keywords_crudas = respuesta.choices[0].message.content.strip()

        if keywords_crudas.count("|") != 2:
            keywords_limpias = "NO_KEYWORDS"
        else:
            keywords_list = [k.strip() for k in keywords_crudas.split("|") if k.strip()]
            if any(len(k) > 25 for k in keywords_list):
                keywords_limpias = "NO_KEYWORDS"
            else:
                keywords_limpias = keywords_crudas

        # Paso 2: Validar resultados
        if keywords_limpias == "NO_KEYWORDS":
            historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
            historial_texto = "".join([f"{m['role']}: {m['content']}\n" for m in historial])

            prompt_reintento = [{
                "role": "system",
                "content": (
                    f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear su anuncio.\n"
                    f"Le pediste que te envíe 3 palabras clave separadas por guiones, pero el mensaje que recibiste fue: \"{mensaje_usuario}\".\n"
                    f"A continuación puedes ver el historial reciente de su conversación:\n\n"
                    f"{historial_texto}\n"
                    "Ahora debes generar una respuesta cálida, humana y natural, como si estuvieras charlando normalmente por WhatsApp.\n\n"
                    "OBLIGATORIAMENTE debes PARAFRASEAR la siguiente idea dentro del mensaje:\n"
                    "'Necesito que me envíes 3 palabras clave separadas por guiones, como en este ejemplo: colchones baratos - camas dobles - almohadas ortopédicas. "
                    "Si deseas, también puedes escribir *CREAR PALABRAS CLAVE* en mayúsculas y yo te ayudaré a generarlas automáticamente para ti. "
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
            if "crear palabras clave" not in mensaje_verificado or "salir" not in mensaje_verificado:
                mensaje_reintento = (
                    "Para continuar necesito que me envíes 3 palabras clave separadas por guiones, como: "
                    "colchones baratos - camas dobles - almohadas ortopédicas. "
                    "También puedes escribir *CREAR PALABRAS CLAVE* en mayúsculas para ayudarte automáticamente. "
                    "Y si deseas salir del proceso, escribe *SALIR* en mayúsculas."
                )

            guardar_mensaje(numero_usuario, "assistant", mensaje_reintento)
            return mensaje_reintento


        # ✅ Keywords válidas
        update_user_field(numero_usuario, "Keywords", keywords_limpias)
        update_user_field(numero_usuario, "Estado Anuncio", "Keywords Registradas")

        print(f"[LOG] Palabras clave registradas correctamente: {keywords_limpias} para número: {numero_usuario}")

        from src.services.FSM.flujo_creacion_campana import ejecutar_flujo_creacion_campana
        return ejecutar_flujo_creacion_campana(numero_usuario)

    except Exception:
        return "Hubo un problema al procesar tus palabras clave. ¿Podrías enviarlas nuevamente por favor?"
