import json
import logging
from datetime import datetime
from telethon import events

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Función para cargar los datos de los usuarios desde el archivo user_data.json
def cargar_datos_usuarios():
    try:
        with open("user_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("Archivo user_data.json no encontrado. Creando un archivo nuevo.")
        return {}
    except json.JSONDecodeError:
        logging.error("Error al decodificar el archivo user_data.json. Verifica el formato.")
        return {}

# Función para guardar los datos de los usuarios en el archivo user_data.json
def guardar_datos_usuarios(datos):
    try:
        with open("user_data.json", "w") as f:
            json.dump(datos, f, indent=4)
    except Exception as e:
        logging.error(f"Error al guardar datos de usuarios: {e}")

# Función para cargar las calificaciones desde el archivo calificaciones.json
def cargar_calificaciones():
    try:
        with open("calificaciones.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("Archivo calificaciones.json no encontrado. Creando un archivo nuevo.")
        return {}
    except json.JSONDecodeError:
        logging.error("Error al decodificar el archivo calificaciones.json. Verifica el formato.")
        return {}

# Función para guardar las calificaciones en el archivo calificaciones.json
def guardar_calificaciones(datos):
    try:
        with open("calificaciones.json", "w") as f:
            json.dump(datos, f, indent=4)
    except Exception as e:
        logging.error(f"Error al guardar calificaciones: {e}")

# Función para añadir 5 coins al usuario registrado por nombre de usuario
def agregar_coins(username, datos_usuarios):
    if username in datos_usuarios:
        # Si el usuario ya existe, incrementamos sus coins
        datos_usuarios[username]["coins"] += 5
        logging.info(f"Se han añadido 5 coins al usuario {username}. Total de coins: {datos_usuarios[username]['coins']}")
    else:
        logging.warning(f"El usuario {username} no está registrado en user_data.json")
    guardar_datos_usuarios(datos_usuarios)  # Guardar inmediatamente después de la modificación

# Función para generar una respuesta personalizada según la calificación
def generar_respuesta(calificacion):
    if calificacion <= 3:
        return "😔 Trabajaré más duro para mejorar. Tu calificación me motiva a seguir mejorando."
    elif 4 <= calificacion <= 5:
        return "😐 Gracias por tu honesta opinión, seguiré trabajando para ofrecer un mejor servicio."
    elif calificacion == 6:
        return "🙂 ¡Gracias por tu feedback positivo! Seguiremos mejorando."
    elif calificacion == 7:
        return "😊 ¡Gracias por tu apoyo! Estamos contentos de que te haya gustado."
    elif calificacion == 8:
        return "😀 ¡Gracias! ¡Estamos en el buen camino gracias a tu calificación!"
    elif calificacion == 9:
        return "😄 ¡Gracias por la excelente puntuación! ¡Trabajaremos para llegar al 10!"
    elif calificacion == 10:
        return "🤩 ¡Perfecto! ¡Gracias por la calificación máxima! Me esforzaré para seguir brindando lo mejor."
    else:
        return "🤔 Por favor, ingresa un número válido entre 1 y 10."

# Función para verificar si el usuario ya ha calificado
def ya_califico(username, calificaciones):
    return username in calificaciones

# Comando para calificar directamente con un número, por ejemplo: /calificar 10
def iniciar_comando_calificar(client):
    @client.on(events.NewMessage(pattern=r'/calificar (\d+)'))
    async def calificar_handler(event):
        user_id = event.sender_id
        username = event.sender.username  # Obtener el nombre de usuario de Telegram
        datos_usuarios = cargar_datos_usuarios()  # Cargar datos de user_data.json
        calificaciones = cargar_calificaciones()  # Cargar datos de calificaciones.json

        # Verificar si el usuario ya ha calificado
        if ya_califico(username, calificaciones):
            await event.respond(f"⚠️ Ya has calificado anteriormente. Gracias por tu participación. 🎉")
            return

        # Obtener la calificación desde el comando
        calificacion_str = event.pattern_match.group(1)
        try:
            calificacion = int(calificacion_str)
            if 1 <= calificacion <= 10:
                # Guardar la calificación del usuario en calificaciones.json
                calificaciones[username] = calificacion
                guardar_calificaciones(calificaciones)
                logging.info(f"Usuario {username} calificó con {calificacion}.")

                # Añadir 5 coins al usuario en user_data.json
                agregar_coins(username, datos_usuarios)

                # Generar respuesta personalizada según la calificación
                respuesta_personalizada = generar_respuesta(calificacion)
                await event.respond(f"{respuesta_personalizada}\n\n🎁 ¡Has recibido 5 coins por tu participación!")
            else:
                await event.respond("⚠️ **Por favor, ingresa un número del 1 al 10.**")
        except ValueError:
            await event.respond("⚠️ **Por favor, ingresa un número válido.**")
            logging.warning(f"Usuario {username} ingresó una calificación no válida: {calificacion_str}.")

# Comando para ver la calificación promedio del bot
def iniciar_comando_ver_calificacion(client):
    @client.on(events.NewMessage(pattern='/vercalificacion'))
    async def ver_calificacion_handler(event):
        calificaciones = cargar_calificaciones()
        if not calificaciones:
            await event.respond("😅 Aún no hay calificaciones.")
        else:
            promedio = sum(calificaciones.values()) / len(calificaciones)
            await event.respond(f"⭐ **Calificación promedio del bot:** {promedio:.2f}/10 basada en {len(calificaciones)} calificaciones.")
            logging.info(f"Se mostró el promedio de calificaciones: {promedio:.2f}.")
