from src.data.chatbot_sheet_connector import get_user_field, update_user_field
from src.services.FSM.get_nombre import procesar_nombre_usuario
from src.services.FSM.get_ciudad import procesar_ciudad_usuario
from src.services.FSM.get_empresa import procesar_nombre_empresa
from src.services.FSM.get_inversion import procesar_monto_inversion
from src.services.FSM.generar_titulos import procesar_generacion_titulos
from src.services.FSM.get_titulos import procesar_titulos_usuario
from src.services.FSM.generar_descripciones import procesar_generacion_descripciones
from src.services.FSM.get_descripciones import procesar_descripciones_usuario
from src.services.FSM.generar_keywords import procesar_generacion_keywords
from src.services.FSM.get_keywords import procesar_keywords_usuario
from src.data.firestore_storage import leer_historial
from src.config import openai_client, GPT_MODEL_AVANZADO, TEMPERATURA_CONVERSACION

def ejecutar_flujo_creacion_campana(numero_usuario, mensaje_usuario=None):
    """
    Controla el flujo conversacional para la creación de una campaña,
    ejecutando funciones específicas según el estado actual.
    """

    estado_campana = get_user_field(numero_usuario, "Estado Campana")
    estado_anuncio = get_user_field(numero_usuario, "Estado Anuncio")

    
    if estado_campana == "no iniciada":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que responde en WhatsApp con un tono cálido, natural y humano.\n"
                "Estos son los últimos mensajes intercambiados: {historial}.\n\n"
                "NO debes empezar la respuesta con saludos como 'Hola', 'Buen día', 'Buenas tardes' ni similares.\n"
                "Debes entrar directamente al mensaje, como si estuvieras continuando una conversación que ya empezó.\n\n"
                "Ahora responde al último mensaje del usuario como si continuaras una conversación real.\n\n"
                "IMPORTANTE: Asegúrate de incluir, con naturalidad y estilo libre, que estás conectado a Google Ads para ayudarle a crear anuncios,\n"
                "y que necesitas su nombre para registrar el avance. Puedes expresarlo como quieras,\n"
                "siempre que ambas ideas estén presentes claramente en la respuesta.\n\n"
                "No repitas lo que dijo el usuario, no agregues explicaciones técnicas y no menciones que estás leyendo historial.\n"
                "Tu respuesta debe ser fluida, cercana y breve, como un mensaje de WhatsApp real, de máximo 5 líneas."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })
                                    
        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )
    
        # Guardamos el estado como "Esperando Nombre"
        update_user_field(numero_usuario, "Estado Campana", "Esperando Nombre")

        # Obtenemos y limpiamos la respuesta generada
        respuesta_texto = respuesta.choices[0].message.content.strip()

        # Verificación para garantizar que incluya las partes obligatorias
        respuesta_verificada = respuesta_texto.lower()

        if "google ads" not in respuesta_verificada or "nombre" not in respuesta_verificada:
            return (
                "Me encuentro conectado a Google Ads para que juntos creemos tus anuncios. "
                "Por favor indicame tu nombre para registrar tu avance en la plataforma."
            )
        else:
            return respuesta_texto


    elif estado_campana == "Esperando Nombre":
        return procesar_nombre_usuario(numero_usuario, mensaje_usuario)

    elif estado_campana == "Nombre Registrado":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que estuvo conversando con un usuario por WhatsApp y actualmente te encuentras conectado con la plataforma de Google Ads para crear su campaña publicitaria.\n"
                "Tu objetivo es continuar esta conversación con total naturalidad, como si no hubiera ninguna interrupción. Usa el historial para mantener el mismo tono y conexión emocional.\n\n"
                "Dentro del mismo mensaje debes integrar, de forma cálida y PARAFRASEADA, la siguiente instrucción:\n"
                "'Por favor dime cómo se llama tu empresa o emprendimiento para que podamos avanzar con tu campaña publicitaria.'\n\n"
                "No dividas en dos bloques. Responde como si estuvieras hablando con empatía, en WhatsApp, de forma continua y real.\n"
                "IMPORTANTE: No menciones que estás leyendo el historial. No repitas textualmente lo que dijo el usuario. Mantente en un máximo de 5 líneas y usa lenguaje humano."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )
    
        # Guardamos el estado como "Esperando Empresa"
        update_user_field(numero_usuario, "Estado Campana", "Esperando Empresa")

        # Limpiamos el mensaje y verificamos que incluya las partes obligatorias
        respuesta_texto = respuesta.choices[0].message.content.strip()
        respuesta_verificada = respuesta_texto.lower()

        if ("empresa" not in respuesta_verificada and 
            "emprendimiento" not in respuesta_verificada and 
            "negocio" not in respuesta_verificada):
            
            return (
                "Para continuar por favor indicame como se llama tu empresa o emprendimiento. "
            )
        else:
            return respuesta_texto


    elif estado_campana == "Esperando Empresa":
        return procesar_nombre_empresa(numero_usuario, mensaje_usuario)

    elif estado_campana == "Empresa Registrada":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que está guiando a un usuario por WhatsApp para configurar su campaña en Google Ads.\n"
                "Ya recibiste el nombre de su negocio y ahora tu tarea es continuar la conversación con total naturalidad y calidez, como si fuera una charla fluida.\n\n"
                "Dentro del mismo mensaje debes integrar, de forma PARAFRASEADA y cálida, la siguiente instrucción:\n"
                "'¿En qué departamento de Bolivia deseas que se muestren tus anuncios? (solo departamento, no ciudad, tampoco region)'\n\n"
                "IMPORTANTE: No repitas lo que dijo el usuario, no menciones que estás leyendo historial. Usa máximo 5 líneas con estilo WhatsApp, cálido y útil."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Esperando Ciudad")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Esperando Ciudad":
        return procesar_ciudad_usuario(numero_usuario, mensaje_usuario)

    elif estado_campana == "Ciudad Registrada":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que estuvo conversando con un usuario por WhatsApp y actualmente estás finalizando la configuración de su campaña publicitaria en Google Ads.\n"
                "Tu objetivo es continuar esta conversación con naturalidad, como si fuera parte de la misma charla, manteniendo el mismo tono cálido y cercano que ya se estableció.\n\n"
                "Dentro del mismo mensaje debes integrar, de forma cálida y PARAFRASEADA, la siguiente instrucción:\n"
                "'¿Cuánto podrías invertir por día en tu campaña publicitaria? Este monto es solo simbólico, no se cobrará nada.'\n\n"
                "IMPORTANTE: No menciones que estás leyendo el historial. No repitas literalmente lo que dijo el usuario. Sé cálido, útil y directo. Usa máximo 5 líneas como en una conversación de WhatsApp."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Esperando Monto")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Esperando Monto":
        return procesar_monto_inversion(numero_usuario, mensaje_usuario)


####################################################################################################################################################################
    elif mensaje_usuario == "CREAR TITULOS" and estado_anuncio == "Esperando Titulos":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear su anuncio.\n"
                f"El usuario ha solicitado que lo ayudes a generar títulos automáticos.\n"
                f"A continuación puedes ver el historial reciente de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes generar una respuesta cálida, natural y fluida, como si estuvieras conversando por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Para poder ayudarte a crear los mejores títulos, necesito que me cuentes de forma breve a qué se dedica tu negocio y cuál es tu principal objetivo con estos anuncios.'\n\n"
                "No repitas textualmente lo que dijo el usuario. No expliques que estás leyendo historial. Usa máximo 5 líneas, con un estilo humano, cálido y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Generando Titulos")
        return respuesta.choices[0].message.content.strip()
    
    elif estado_campana == "Campana Complete" and estado_anuncio == "Generando Titulos":
        return procesar_generacion_titulos(numero_usuario, mensaje_usuario)

                #...........................................................................................................................
    elif estado_campana == "Monto Registrado" and estado_anuncio == "no iniciado":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que acaba de finalizar la creación de una campaña publicitaria.\n"
                "Ahora debes continuar la conversación de forma cálida, natural y fluida, como si estuvieras hablando por WhatsApp.\n\n"
                "Debes PARAFRASEAR OBIGATORIAMENTE dentro del mensaje la siguiente solicitud:\n"
                "'Para completar tu anuncio, por favor envíame 3 títulos separados por un guion. Ejemplo: Gran oferta - Compra fácil - Promoción especial'\n\n"
                "IMPORTANTE: No repitas textualmente lo que dijo el usuario. No digas que estás leyendo historial. Usa máximo 5 líneas de WhatsApp, con un tono humano y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Campana Complete")
        update_user_field(numero_usuario, "Validation Status", "incomplete")
        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Titulos")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Campana Complete" and estado_anuncio == "Esperando Titulos":
        return procesar_titulos_usuario(numero_usuario, mensaje_usuario)

                #...........................................................................................................................


    elif estado_campana == "Campana Complete" and estado_anuncio == "Titulos Generados":

        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        # Recuperar los títulos generados
        titulos_generados = get_user_field(numero_usuario, "Titles")
        if titulos_generados:
            titulos_list = titulos_generados.split("|")
            # Crear lista con saltos de línea
            titulos_mostrados = "\n".join(f"• {titulo.strip()}" for titulo in titulos_list)
        else:
            titulos_mostrados = "• No se encontraron títulos registrados."

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        # Parte estática: mostrar títulos ya registrados (con espacio en blanco después)
        mensaje_estatico = (
            f"¡Gracias por confiar en mí! 🙌\n"
            f"Estos son los títulos que registré para tu anuncio:\n"
            f"{titulos_mostrados}\n\n"  # <--- salto extra agregado aquí
        )

        # Construcción final del prompt
        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n\n"
                "Estos son los últimos mensajes intercambiados:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes responder de forma cálida, humana y fluida como si siguieras la charla normalmente.\n\n"
                "IMPORTANTE:\n"
                "- RESPONDE exactamente primero con este fragmento estático sin cambios:\n\n"
                f"{mensaje_estatico}"
                "- Luego PARAFRASEA obligatoriamente esta solicitud:\n"
                "'Ahora, por favor envíame 3 descripciones separadas por guiones. Ejemplo: Somos los mejores en la ciudad - Contáctate con nosotros - Descuentos por tiempo limitado.'\n\n"
                "No expliques tu proceso. No repitas literal el texto. No digas que estás leyendo historial. Usa máximo 5 líneas."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=300
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Descripciones")
        return respuesta.choices[0].message.content.strip()




    
    elif estado_campana == "Campana Complete" and estado_anuncio == "Titulos Registrados":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n"
                "Ya tienes registrados los títulos publicitarios, y ahora tu tarea es continuar la conversación de forma cálida, natural y fluida, como si estuvieras charlando normalmente por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Ahora para seguir avanzando, por favor envíame 3 descripciones cortas separadas por un guion. Ejemplo: Compra fácil - Entrega inmediata - Calidad garantizada.'\n\n"
                "IMPORTANTE: No repitas textualmente el mensaje, no digas que estás leyendo historial. Usa máximo 5 líneas, con un estilo humano, cálido y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=250
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Descripciones")
        return respuesta.choices[0].message.content.strip()

####################################################################################################################################################################
    elif mensaje_usuario == "CREAR DESCRIPCIONES" and estado_anuncio == "Esperando Descripciones":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n"
                f"El usuario ha solicitado que lo ayudes a generar descripciones automáticas para su anuncio.\n"
                f"A continuación puedes ver el historial reciente de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes generar una respuesta cálida, natural y fluida, como si estuvieras conversando por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Para ayudarte a crear buenas descripciones, necesito que me cuentes cuál es tu producto o servicio más importante, "
                "y qué beneficio lo hace especial o diferente frente a otros negocios.'\n\n"
                "No repitas textualmente lo que dijo el usuario. No expliques que estás leyendo historial. Usa máximo 5 líneas, con un estilo humano, cálido y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Generando Descripciones")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Campana Complete" and estado_anuncio == "Generando Descripciones":
        return procesar_generacion_descripciones(numero_usuario, mensaje_usuario)

                #...........................................................................................................................

    elif estado_campana == "Campana Complete" and estado_anuncio == "Titulos Registrados":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que ya ha completado la creación de una campaña y los títulos del anuncio.\n"
                "Ahora debes continuar la conversación de forma cálida, natural y fluida, como si estuvieras hablando por WhatsApp.\n\n"
                "Debes PARAFRASEAR OBLIGATORIAMENTE dentro del mensaje la siguiente solicitud:\n"
                "'Para seguir con tu anuncio, por favor envíame 3 descripciones separadas por un guion. Ejemplo: Muebles de calidad - Entrega rápida - Diseño elegante'\n\n"
                "IMPORTANTE: No repitas textualmente lo que dijo el usuario. No digas que estás leyendo historial. Usa máximo 5 líneas de WhatsApp, con un tono humano y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Descripciones")
        return respuesta.choices[0].message.content.strip()
    
    elif estado_campana == "Campana Complete" and estado_anuncio == "Esperando Descripciones":
        return procesar_descripciones_usuario(numero_usuario, mensaje_usuario)

                #...........................................................................................................................

    elif estado_campana == "Campana Complete" and estado_anuncio == "Descripciones Generadas":

        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        # Recuperar las descripciones generadas
        descripciones_generadas = get_user_field(numero_usuario, "Descriptions")
        if descripciones_generadas:
            descripciones_list = descripciones_generadas.split("|")
            descripciones_mostradas = "\n".join(f"• {desc.strip()}" for desc in descripciones_list)
        else:
            descripciones_mostradas = "• No se encontraron descripciones registradas."

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        # Parte estática para mostrar descripciones
        mensaje_estatico = (
            f"¡Perfecto! 🙌 Estas son las descripciones que preparé para tu anuncio:\n"
            f"{descripciones_mostradas}\n\n"
        )

        # Construcción del prompt con instrucciones
        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n\n"
                "Estos son los últimos mensajes intercambiados:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes responder de forma cálida, humana y fluida como si siguieras la charla normalmente.\n\n"
                "IMPORTANTE:\n"
                "- RESPONDE exactamente primero con este fragmento estático sin cambios:\n\n"
                f"{mensaje_estatico}"
                "- Luego PARAFRASEA obligatoriamente esta solicitud:\n"
                "'Para seguir afinando tu anuncio, por favor dime 3 *palabras clave* separadas por guiones que ayuden a que los clientes encuentren fácilmente tu negocio en Google. Ejemplo: Ropero - Servicio legal - Celular.'\n\n"
                "No expliques tu proceso. No repitas literal el texto. No digas que estás leyendo historial. Usa máximo 5 líneas."
            )
        })


        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=300
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Keywords")
        return respuesta.choices[0].message.content.strip()
    

    elif estado_campana == "Campana Complete" and estado_anuncio == "Descripciones Registradas":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n"
                "Ya tienes registradas las descripciones publicitarias, y ahora tu tarea es continuar la conversación de forma cálida, natural y fluida, como si estuvieras charlando normalmente por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Ahora para seguir afinando tu anuncio, por favor dime 3 *palabras clave* separadas por guiones que ayuden a que los clientes encuentren fácilmente tu negocio en Google. Ejemplo: Ropero - Servicio legal - Celular.'\n\n"
                "IMPORTANTE: No repitas textualmente el mensaje, no digas que estás leyendo historial. Usa máximo 5 líneas, con un estilo humano, cálido y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=250
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Keywords")
        return respuesta.choices[0].message.content.strip()

####################################################################################################################################################################
    elif mensaje_usuario == "CREAR PALABRAS CLAVE" and estado_anuncio == "Esperando Keywords":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n"
                f"El usuario ha solicitado que lo ayudes a generar palabras clave automáticas para su anuncio.\n"
                f"A continuación puedes ver el historial reciente de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes generar una respuesta cálida, natural y fluida, como si estuvieras conversando por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'¿Qué productos o servicios vendes y qué tipo de personas quieres que encuentren tu anuncio, para que podamos encontrar las mejores palabras para ti.'\n\n"
                "No repitas textualmente lo que dijo el usuario. No expliques que estás leyendo historial. Usa máximo 5 líneas, con un estilo humano, cálido y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Generando Keywords")
        return respuesta.choices[0].message.content.strip()
    
    elif estado_campana == "Campana Complete" and estado_anuncio == "Generando Keywords":
        return procesar_generacion_keywords(numero_usuario, mensaje_usuario)


                #...........................................................................................................................
    elif estado_campana == "Campana Complete" and estado_anuncio == "Descripciones Registradas":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que ya ha completado la creación de una campaña, los títulos y las descripciones del anuncio.\n"
                "Ahora debes continuar la conversación de forma cálida, natural y fluida, como si estuvieras hablando por WhatsApp.\n\n"
                "Debes PARAFRASEAR OBLIGATORIAMENTE dentro del mensaje la siguiente solicitud:\n"
                "'Para seguir con tu anuncio, por favor envíame 3 *palabras clave* separadas por un guion. Ejemplo: colchones - camas - almohadas'\n\n"
                "IMPORTANTE: No repitas textualmente lo que dijo el usuario. No digas que estás leyendo historial. Usa máximo 5 líneas de WhatsApp, con un tono humano y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Keywords")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Campana Complete" and estado_anuncio == "Esperando Keywords":
        return procesar_keywords_usuario(numero_usuario, mensaje_usuario)


                #...........................................................................................................................
    elif estado_campana == "Campana Complete" and estado_anuncio == "Keywords Generadas":

        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        # Recuperar las palabras clave generadas
        keywords_generadas = get_user_field(numero_usuario, "Keywords")
        if keywords_generadas:
            keywords_list = keywords_generadas.split("|")
            keywords_mostradas = "\n".join(f"• {kw.strip()}" for kw in keywords_list)
        else:
            keywords_mostradas = "• No se encontraron palabras clave registradas."

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        # Parte estática para mostrar las palabras clave
        mensaje_estatico = (
            f"¡Genial! 🎉 Estas son las palabras clave que registramos para tu anuncio:\n"
            f"{keywords_mostradas}\n\n"
        )

        # Construcción del prompt final
        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n\n"
                "Estos son los últimos mensajes intercambiados:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes responder de forma cálida, humana y fluida como si siguieras la charla normalmente.\n\n"
                "IMPORTANTE:\n"
                "- RESPONDE exactamente primero con este fragmento estático sin cambios:\n\n"
                f"{mensaje_estatico}"
                "- Luego PARAFRASEA obligatoriamente esta idea:\n"
                "'¡Felicidades! 🎯 Has completado exitosamente la creación de tus anuncios en Google Ads. Pronto estará activo para ayudarte a conseguir más clientes.'\n\n"
                "No expliques tu proceso. No repitas literal el texto. No digas que estás leyendo historial. Usa máximo 5 líneas."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=300
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Anuncio Completed")
        return respuesta.choices[0].message.content.strip()
    
    elif estado_campana == "Campana Complete" and estado_anuncio == "Keywords Registradas":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear su anuncio.\n"
                "Ya se han registrado los títulos, descripciones y palabras clave, por lo que has llegado al final del proceso de creación de anuncios en Google Ads.\n\n"
                "Ahora debes generar un mensaje cálido, humano y fluido como si estuvieras conversando normalmente por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'¡Felicidades! Has finalizado con éxito la creación de tus anuncios en Google Ads. Muy pronto estará activo y solo espera a que te contacten más clientes.'\n\n"
                "IMPORTANTE: No repitas textualmente el mensaje. No digas que estás leyendo historial. Usa máximo 5 líneas con tono humano, agradecido, profesional y amigable. "
                "Debe quedar claro que el anuncio ya fue creado, estará activo pronto, y que te enviará una imagen de muestra."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_AVANZADO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=250
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Anuncio Completed")
        return respuesta.choices[0].message.content.strip()









'''
from src.data.chatbot_sheet_connector import get_user_field, update_user_field
from src.services.FSM.get_nombre import procesar_nombre_usuario
from src.services.FSM.get_ciudad import procesar_ciudad_usuario
from src.services.FSM.get_empresa import procesar_nombre_empresa
from src.services.FSM.get_inversion import procesar_monto_inversion
from src.services.FSM.get_titulos import procesar_titulos_usuario
from src.services.FSM.generar_titulos import procesar_generacion_titulos
from src.data.firestore_storage import leer_historial
from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_CONVERSACION

def ejecutar_flujo_creacion_campana(numero_usuario, mensaje_usuario=None):
    """
    Controla el flujo conversacional para la creación de una campaña,
    ejecutando funciones específicas según el estado actual.
    """

    estado_campana = get_user_field(numero_usuario, "Estado Campana")
    estado_anuncio = get_user_field(numero_usuario, "Estado Anuncio")

    if estado_campana == "no iniciada":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que estuvo conversando con un usuario por WhatsApp.\n"
                "Estos son los últimos mensajes intercambiados entre ustedes: {historial}.\n"
                "Tu tarea ahora es responder al último mensaje del usuario con NATURALIDAD, utilizando un estilo cálido y humano propio de WhatsApp.\n\n"
                "IMPORTANTE: debes PARAFRASEAR OBLIGATORIAMENTE el siguiente contenido como parte del mensaje de bienvenida:\n"
                "'BIENVENIDO A GOOGLE ADS, me encuentro conectado a la plataforma para que podamos crear tus anuncios. Por favor dime tu nombre para poder registrar tu avance en Google.'\n\n"
                "No menciones que estás leyendo mensajes previos. No repitas lo que dijo el usuario. No agregues explicaciones innecesarias.\n"
                "Solo responde de forma fluida y cercana como si continuaras una conversación normal. Usa máximo 5 líneas."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Esperando Nombre")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Esperando Nombre":
        return procesar_nombre_usuario(numero_usuario, mensaje_usuario)

    elif estado_campana == "Nombre Registrado":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que estuvo conversando con un usuario por WhatsApp y actualmente te encuentras conectado con la plataforma de Google Ads para crear su campaña publicitaria.\n"
                "Tu objetivo es continuar esta conversación con total naturalidad, como si no hubiera ninguna interrupción. Usa el historial para mantener el mismo tono y conexión emocional.\n\n"
                "Dentro del mismo mensaje debes integrar, de forma cálida y PARAFRASEADA, la siguiente instrucción:\n"
                "'Por favor dime cómo se llama tu empresa o emprendimiento para que podamos avanzar con tu campaña publicitaria.'\n\n"
                "No dividas en dos bloques. Responde como si estuvieras hablando con empatía, en WhatsApp, de forma continua y real.\n"
                "IMPORTANTE: No menciones que estás leyendo el historial. No repitas textualmente lo que dijo el usuario. Mantente en un máximo de 5 líneas y usa lenguaje humano."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Esperando Empresa")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Esperando Empresa":
        return procesar_nombre_empresa(numero_usuario, mensaje_usuario)

    elif estado_campana == "Empresa Registrada":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que está guiando a un usuario por WhatsApp para configurar su campaña en Google Ads.\n"
                "Ya recibiste el nombre de su negocio y ahora tu tarea es continuar la conversación con total naturalidad y calidez, como si fuera una charla fluida.\n\n"
                "Dentro del mismo mensaje debes integrar, de forma PARAFRASEADA y cálida, la siguiente instrucción:\n"
                "'¿En qué ciudad o departamento de Bolivia deseas que se muestren tus anuncios?'\n\n"
                "IMPORTANTE: No repitas lo que dijo el usuario, no menciones que estás leyendo historial. Usa máximo 5 líneas con estilo WhatsApp, cálido y útil."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Esperando Ciudad")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Esperando Ciudad":
        return procesar_ciudad_usuario(numero_usuario, mensaje_usuario)

    elif estado_campana == "Ciudad Registrada":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que estuvo conversando con un usuario por WhatsApp y actualmente estás finalizando la configuración de su campaña publicitaria en Google Ads.\n"
                "Tu objetivo es continuar esta conversación con naturalidad, como si fuera parte de la misma charla, manteniendo el mismo tono cálido y cercano que ya se estableció.\n\n"
                "Dentro del mismo mensaje debes integrar, de forma cálida y PARAFRASEADA, la siguiente instrucción:\n"
                "'¿Cuánto podrías invertir por día en tu campaña publicitaria? Este monto es solo simbólico, no se cobrará nada.'\n\n"
                "IMPORTANTE: No menciones que estás leyendo el historial. No repitas literalmente lo que dijo el usuario. Sé cálido, útil y directo. Usa máximo 5 líneas como en una conversación de WhatsApp."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Esperando Monto")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Esperando Monto":
        return procesar_monto_inversion(numero_usuario, mensaje_usuario)


    elif mensaje_usuario == "CREAR TITULOS" and estado_anuncio == "Esperando Titulos":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear su anuncio.\n"
                f"El usuario ha solicitado que lo ayudes a generar títulos automáticos.\n"
                f"A continuación puedes ver el historial reciente de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes generar una respuesta cálida, natural y fluida, como si estuvieras conversando por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Para poder ayudarte a crear los mejores títulos, necesito que me cuentes de forma breve a qué se dedica tu negocio y cuál es tu principal objetivo con estos anuncios.'\n\n"
                "No repitas textualmente lo que dijo el usuario. No expliques que estás leyendo historial. Usa máximo 5 líneas, con un estilo humano, cálido y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Generando Titulos")
        return respuesta.choices[0].message.content.strip()
    
    elif estado_campana == "Campana Complete" and estado_anuncio == "Generando Titulos":
        return procesar_generacion_titulos(numero_usuario, mensaje_usuario)


    elif estado_campana == "Monto Registrado" and estado_anuncio == "no iniciado":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que acaba de finalizar la creación de una campaña publicitaria.\n"
                "Ahora debes continuar la conversación de forma cálida, natural y fluida, como si estuvieras hablando por WhatsApp.\n\n"
                "Debes PARAFRASEAR OBIGATORIAMENTE dentro del mensaje la siguiente solicitud:\n"
                "'Para completar tu anuncio, por favor envíame 3 títulos separados por un guion. Ejemplo: Gran oferta - Compra fácil - Promoción especial'\n\n"
                "IMPORTANTE: No repitas textualmente lo que dijo el usuario. No digas que estás leyendo historial. Usa máximo 5 líneas de WhatsApp, con un tono humano y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Campana Complete")
        update_user_field(numero_usuario, "Validation Status", "incomplete")
        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Titulos")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Campana Complete" and estado_anuncio == "Esperando Titulos":
        return procesar_titulos_usuario(numero_usuario, mensaje_usuario)


    elif estado_campana == "Campana Complete" and estado_anuncio == "Titulos Generados":

        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        # Recuperar los títulos generados
        titulos_generados = get_user_field(numero_usuario, "Titles")
        if titulos_generados:
            titulos_list = titulos_generados.split("|")
            # Crear lista con saltos de línea
            titulos_mostrados = "\n".join(f"- {titulo.strip()}" for titulo in titulos_list)
        else:
            titulos_mostrados = "- No se encontraron títulos registrados."

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        # Parte estática: mostrar títulos ya registrados
        mensaje_estatico = (
            f"¡Gracias por confiar en mí! 🙌\n"
            f"Estos son los títulos que registré para tu anuncio:\n"
            f"{titulos_mostrados}\n\n"
        )

        # Construcción final del prompt
        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n\n"
                "Estos son los últimos mensajes intercambiados:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes responder de forma cálida, humana y fluida como si siguieras la charla normalmente.\n\n"
                "IMPORTANTE:\n"
                "- RESPONDE exactamente primero con este fragmento estático sin cambios:\n\n"
                f"{mensaje_estatico}\n"
                "- Luego PARAFRASEA obligatoriamente esta solicitud:\n"
                "'Ahora, por favor envíame 3 descripciones separadas por guiones. Ejemplo: Somos los mejores en la ciudad - Contáctate con nosotros - Descuentos por tiempo limitado.'\n\n"
                "No expliques tu proceso. No repitas literal el texto. No digas que estás leyendo historial. Usa máximo 5 líneas."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=300
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Descripciones")
        return respuesta.choices[0].message.content.strip()



    
    elif estado_campana == "Campana Complete" and estado_anuncio == "Titulos Registrados":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n"
                "Ya tienes registrados los títulos publicitarios, y ahora tu tarea es continuar la conversación de forma cálida, natural y fluida, como si estuvieras charlando normalmente por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Ahora para seguir avanzando, por favor envíame 3 descripciones cortas separadas por un guion. Ejemplo: Compra fácil - Entrega inmediata - Calidad garantizada.'\n\n"
                "IMPORTANTE: No repitas textualmente el mensaje, no digas que estás leyendo historial. Usa máximo 5 líneas, con un estilo humano, cálido y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=250
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Descripciones")
        return respuesta.choices[0].message.content.strip()






















    elif estado_campana == "Campana Complete" and estado_anuncio == "Titulos Generados":

        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        # Recuperar los títulos generados
        titulos_generados = get_user_field(numero_usuario, "Titles")
        if titulos_generados:
            # Separar títulos por "|", luego formatearlos en lista con saltos
            titulos_list = titulos_generados.split("|")
            titulos_mostrados = "\n".join(f"- {titulo.strip()}" for titulo in titulos_list)
        else:
            titulos_mostrados = "No se encontraron títulos registrados."

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n\n"
                "Estos son los últimos mensajes de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes responder de forma cálida, natural y fluida, como si siguieras charlando con el usuario por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes integrar dentro del mismo mensaje, de forma PARAFRASEADA y en orden, las siguientes ideas:\n\n"
                "1. Agradecer al usuario y mencionar que ya registraste estos títulos para su anuncio:\n"
                f"{titulos_mostrados}\n\n"
                "2. Indicar amablemente que para continuar necesita enviarte 3 descripciones separadas por un guion.\n"
                "3. Brindar este ejemplo para ayudarle: Somos los mejores en la ciudad - Contáctate con nosotros - Descuentos por tiempo limitado.\n\n"
                "IMPORTANTE:\n"
                "- No repitas literalmente estas instrucciones.\n"
                "- No digas que estás leyendo historial.\n"
                "- No expliques tu proceso.\n"
                "- Usa máximo 5 líneas, con estilo cálido, humano y fluido propio de WhatsApp."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=300
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Descripciones")
        return respuesta.choices[0].message.content.strip()






























from src.data.chatbot_sheet_connector import get_user_field, update_user_field
from src.services.FSM.get_nombre import procesar_nombre_usuario
from src.services.FSM.get_ciudad import procesar_ciudad_usuario
from src.services.FSM.get_empresa import procesar_nombre_empresa
from src.services.FSM.get_inversion import procesar_monto_inversion
from src.services.FSM.get_titulos import procesar_titulos_usuario
from src.services.FSM.generar_titulos import procesar_generacion_titulos
from src.data.firestore_storage import leer_historial
from src.config import openai_client, GPT_MODEL_PRECISO, TEMPERATURA_CONVERSACION

def ejecutar_flujo_creacion_campana(numero_usuario, mensaje_usuario=None):
    """
    Controla el flujo conversacional para la creación de una campaña,
    ejecutando funciones específicas según el estado actual.
    """

    estado_campana = get_user_field(numero_usuario, "Estado Campana")
    estado_anuncio = get_user_field(numero_usuario, "Estado Anuncio")

    if estado_campana == "no iniciada":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que estuvo conversando con un usuario por WhatsApp.\n"
                "Estos son los últimos mensajes intercambiados entre ustedes: {historial}.\n"
                "Tu tarea ahora es responder al último mensaje del usuario con NATURALIDAD, utilizando un estilo cálido y humano propio de WhatsApp.\n\n"
                "IMPORTANTE: debes PARAFRASEAR OBLIGATORIAMENTE el siguiente contenido como parte del mensaje de bienvenida:\n"
                "'BIENVENIDO A GOOGLE ADS, me encuentro conectado a la plataforma para que podamos crear tus anuncios. Por favor dime tu nombre para poder registrar tu avance en Google.'\n\n"
                "No menciones que estás leyendo mensajes previos. No repitas lo que dijo el usuario. No agregues explicaciones innecesarias.\n"
                "Solo responde de forma fluida y cercana como si continuaras una conversación normal. Usa máximo 5 líneas."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Esperando Nombre")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Esperando Nombre":
        return procesar_nombre_usuario(numero_usuario, mensaje_usuario)

    elif estado_campana == "Nombre Registrado":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que estuvo conversando con un usuario por WhatsApp y actualmente te encuentras conectado con la plataforma de Google Ads para crear su campaña publicitaria.\n"
                "Tu objetivo es continuar esta conversación con total naturalidad, como si no hubiera ninguna interrupción. Usa el historial para mantener el mismo tono y conexión emocional.\n\n"
                "Dentro del mismo mensaje debes integrar, de forma cálida y PARAFRASEADA, la siguiente instrucción:\n"
                "'Por favor dime cómo se llama tu empresa o emprendimiento para que podamos avanzar con tu campaña publicitaria.'\n\n"
                "No dividas en dos bloques. Responde como si estuvieras hablando con empatía, en WhatsApp, de forma continua y real.\n"
                "IMPORTANTE: No menciones que estás leyendo el historial. No repitas textualmente lo que dijo el usuario. Mantente en un máximo de 5 líneas y usa lenguaje humano."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Esperando Empresa")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Esperando Empresa":
        return procesar_nombre_empresa(numero_usuario, mensaje_usuario)

    elif estado_campana == "Empresa Registrada":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que está guiando a un usuario por WhatsApp para configurar su campaña en Google Ads.\n"
                "Ya recibiste el nombre de su negocio y ahora tu tarea es continuar la conversación con total naturalidad y calidez, como si fuera una charla fluida.\n\n"
                "Dentro del mismo mensaje debes integrar, de forma PARAFRASEADA y cálida, la siguiente instrucción:\n"
                "'¿En qué ciudad o departamento de Bolivia deseas que se muestren tus anuncios?'\n\n"
                "IMPORTANTE: No repitas lo que dijo el usuario, no menciones que estás leyendo historial. Usa máximo 5 líneas con estilo WhatsApp, cálido y útil."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Esperando Ciudad")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Esperando Ciudad":
        return procesar_ciudad_usuario(numero_usuario, mensaje_usuario)

    elif estado_campana == "Ciudad Registrada":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable que estuvo conversando con un usuario por WhatsApp y actualmente estás finalizando la configuración de su campaña publicitaria en Google Ads.\n"
                "Tu objetivo es continuar esta conversación con naturalidad, como si fuera parte de la misma charla, manteniendo el mismo tono cálido y cercano que ya se estableció.\n\n"
                "Dentro del mismo mensaje debes integrar, de forma cálida y PARAFRASEADA, la siguiente instrucción:\n"
                "'¿Cuánto podrías invertir por día en tu campaña publicitaria? Este monto es solo simbólico, no se cobrará nada.'\n\n"
                "IMPORTANTE: No menciones que estás leyendo el historial. No repitas literalmente lo que dijo el usuario. Sé cálido, útil y directo. Usa máximo 5 líneas como en una conversación de WhatsApp."
            ).replace("{historial}", "\n".join([f"{h['role']}: {h['content']}" for h in historial]))
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Esperando Monto")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Esperando Monto":
        return procesar_monto_inversion(numero_usuario, mensaje_usuario)


    elif mensaje_usuario == "CREAR TITULOS" and estado_anuncio == "Esperando Titulos":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                f"Eres un chatbot profesional conectado con Google Ads que está ayudando a un usuario por WhatsApp a crear su anuncio.\n"
                f"El usuario ha solicitado que lo ayudes a generar títulos automáticos.\n"
                f"A continuación puedes ver el historial reciente de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes generar una respuesta cálida, natural y fluida, como si estuvieras conversando por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Para poder ayudarte a crear los mejores títulos, necesito que me cuentes de forma breve a qué se dedica tu negocio y cuál es tu principal objetivo con estos anuncios.'\n\n"
                "No repitas textualmente lo que dijo el usuario. No expliques que estás leyendo historial. Usa máximo 5 líneas, con un estilo humano, cálido y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Generando Titulos")
        return respuesta.choices[0].message.content.strip()
    
    elif estado_campana == "Campana Complete" and estado_anuncio == "Generando Titulos":
        return procesar_generacion_titulos(numero_usuario, mensaje_usuario)


    elif estado_campana == "Monto Registrado" and estado_anuncio == "no iniciado":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que acaba de finalizar la creación de una campaña publicitaria.\n"
                "Ahora debes continuar la conversación de forma cálida, natural y fluida, como si estuvieras hablando por WhatsApp.\n\n"
                "Debes PARAFRASEAR OBIGATORIAMENTE dentro del mensaje la siguiente solicitud:\n"
                "'Para completar tu anuncio, por favor envíame 3 títulos separados por un guion. Ejemplo: Gran oferta - Compra fácil - Promoción especial'\n\n"
                "IMPORTANTE: No repitas textualmente lo que dijo el usuario. No digas que estás leyendo historial. Usa máximo 5 líneas de WhatsApp, con un tono humano y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=200
        )

        update_user_field(numero_usuario, "Estado Campana", "Campana Complete")
        update_user_field(numero_usuario, "Validation Status", "incomplete")
        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Titulos")
        return respuesta.choices[0].message.content.strip()

    elif estado_campana == "Campana Complete" and estado_anuncio == "Esperando Titulos":
        return procesar_titulos_usuario(numero_usuario, mensaje_usuario)

    elif estado_campana == "Campana Complete" and estado_anuncio == "Titulos Generados":

        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        # Recuperar los títulos generados
        titulos_generados = get_user_field(numero_usuario, "Titles")
        if titulos_generados:
            # Separar títulos por "|", luego formatearlos en lista con saltos
            titulos_list = titulos_generados.split("|")
            titulos_mostrados = "\n".join(f"- {titulo.strip()}" for titulo in titulos_list)
        else:
            titulos_mostrados = "No se encontraron títulos registrados."

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n\n"
                "Estos son los últimos mensajes de su conversación:\n\n"
                f"{historial_texto}\n\n"
                "Ahora debes responder de forma cálida, natural y fluida, como si siguieras charlando con el usuario por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes integrar dentro del mismo mensaje, de forma PARAFRASEADA y en orden, las siguientes ideas:\n\n"
                "1. Agradecer y mencionar que ya registraste estos títulos para su anuncio:\n"
                f"{titulos_mostrados}\n\n"
                "2. Indicar amablemente que para continuar necesita enviarte 3 descripciones separadas por un guion.\n"
                "3. Brindar este ejemplo para ayudarle: Somos los mejores en la ciudad - Contáctate con nosotros - Descuentos por tiempo limitado.\n\n"
                "IMPORTANTE:\n"
                "- No repitas literalmente estas instrucciones.\n"
                "- No digas que estás leyendo historial.\n"
                "- No expliques tu proceso.\n"
                "- Usa máximo 5 líneas, con estilo cálido, humano y fluido propio de WhatsApp."
            )
        })


        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=300
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Descripciones")
        return respuesta.choices[0].message.content.strip()
    
    elif estado_campana == "Campana Complete" and estado_anuncio == "Titulos Registrados":
        historial = leer_historial(numero_usuario, max_user=3, max_bot=3)
        mensajes = []

        for h in historial:
            mensajes.append({"role": h["role"], "content": h["content"]})

        historial_texto = "\n".join([f"{h['role']}: {h['content']}" for h in historial])

        mensajes.insert(0, {
            "role": "system",
            "content": (
                "Eres un chatbot profesional y amable conectado con Google Ads que está ayudando a un usuario por WhatsApp a completar su anuncio.\n"
                "Ya tienes registrados los títulos publicitarios, y ahora tu tarea es continuar la conversación de forma cálida, natural y fluida, como si estuvieras charlando normalmente por WhatsApp.\n\n"
                "OBLIGATORIAMENTE debes PARAFRASEAR dentro del mensaje la siguiente idea:\n"
                "'Ahora para seguir avanzando, por favor envíame 3 descripciones cortas separadas por un guion. Ejemplo: Compra fácil - Entrega inmediata - Calidad garantizada.'\n\n"
                "IMPORTANTE: No repitas textualmente el mensaje, no digas que estás leyendo historial. Usa máximo 5 líneas, con un estilo humano, cálido y de acompañamiento."
            )
        })

        respuesta = openai_client.chat.completions.create(
            model=GPT_MODEL_PRECISO,
            messages=mensajes,
            temperature=TEMPERATURA_CONVERSACION,
            max_tokens=250
        )

        update_user_field(numero_usuario, "Estado Anuncio", "Esperando Descripciones")
        return respuesta.choices[0].message.content.strip()
'''