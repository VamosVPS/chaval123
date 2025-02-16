import json
from datetime import datetime, timedelta
from collections import defaultdict
from telethon import events, Button
import logging

# Limite de comandos free por día
FREE_COMMAND_LIMIT = 5

# Diccionario para rastrear el uso diario de comandos free
daily_command_usage = defaultdict(int)

# Configura el logger
logging.basicConfig(filename='bot_activity.log', level=logging.INFO)

# Función para cargar y guardar datos de usuarios
def load_user_data():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open('user_data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Función para manejar el comando /start
async def handle_start(event, client):
    sender = await event.get_sender()
    username = sender.username
    user_data = load_user_data()

    if username not in user_data:
        await event.reply("Veo que no estás registrado. Usa /register para hacerlo.", parse_mode='markdown')
        user_data[username] = {
            "registered": True,
            "coins": 0,
            "premium_end": None,
            "daily_commands_used": 0,
            "registration_date": datetime.now().strftime('%Y-%m-%d')
        }
        save_user_data(user_data)
        await event.reply("Para ver los comandos free, escribe /cmds.", parse_mode='markdown')
    else:
        await event.reply("Ya estás registrado. Para ver los comandos free, escribe /cmds.", parse_mode='markdown')

    logging.info(f"Usuario {username} registrado o verificado a las {datetime.now()}")

# Función para manejar el comando /cmds
async def handle_cmds(event):
    sender = await event.get_sender()
    username = sender.username
    user_data = load_user_data().get(username, {})

    # Verificar si el usuario está registrado
    if not user_data.get("registered"):
        await event.reply("Veo que no estás registrado. Usa /register para hacerlo.", parse_mode='markdown')
        return

    # Mostrar los comandos free disponibles con instrucciones
    await event.reply(
        "Comandos Free disponibles:\n\n"
        "🔹 /tel [DNI o Número de Teléfono] - Buscar titular de una línea\n"
        "   Ejemplo: `/tel 987654321`\n\n"
        "🔹 /nm [Nombre Completo] - Buscar DNI por nombre\n"
        "   Ejemplo: `/nm Juan Perez`",
        parse_mode='markdown'
    )

    logging.info(f"Usuario {username} solicitó lista de comandos free a las {datetime.now()}")

# Función para manejar comandos free con validación
async def handle_free_command(event, command, client):
    sender = await event.get_sender()
    username = sender.username
    user_data = load_user_data()

    # Verificar si el usuario está registrado
    if not user_data.get(username, {}).get("registered"):
        await event.reply("Veo que no estás registrado. Usa /register para hacerlo.", parse_mode='markdown')
        return

    # Verificar el uso diario de comandos
    today = datetime.now().strftime('%Y-%m-%d')
    if user_data[username].get("last_command_date") != today:
        user_data[username]["daily_commands_used"] = 0
        user_data[username]["last_command_date"] = today

    if user_data[username]["daily_commands_used"] >= FREE_COMMAND_LIMIT:
        await event.reply(
            "🚀 **Has alcanzado el límite diario de comandos free!**\n\n"
            "🔓 **Obtén acceso a muchos más comandos y funcionalidades premium contactando a** @akdios123!",
            parse_mode='markdown'
        )
        logging.info(f"Usuario {username} alcanzó el límite de comandos free a las {datetime.now()}")
        return

    # Validación del comando y formato
    args = event.message.text.split()[1:]
    if command.startswith('/tel'):
        if len(args) != 1 or not args[0].isdigit():
            await event.reply("⚠️ **Formato incorrecto. Usa** `/tel [DNI o Número de Teléfono]`", parse_mode='markdown')
            return
    elif command.startswith('/nm'):
        if len(args) < 2:
            await event.reply("⚠️ **Formato incorrecto. Usa** `/nm [Nombre Completo]`", parse_mode='markdown')
            return

    # Simulación de la ejecución del comando
    await event.reply(f"Ejecutando {command}...", parse_mode='markdown')

    # Incrementar el contador de comandos usados y notificar
    user_data[username]["daily_commands_used"] += 1
    save_user_data(user_data)
    
    commands_left = FREE_COMMAND_LIMIT - user_data[username]["daily_commands_used"]
    await event.reply(f"Te quedan {commands_left} comandos free hoy.", parse_mode='markdown')

    logging.info(f"Usuario {username} ejecutó {command} con {commands_left} comandos restantes a las {datetime.now()}")

# Función para manejar comandos premium
async def handle_premium_command(event, command, client):
    sender = await event.get_sender()
    username = sender.username
    user_data = load_user_data().get(username, {})

    premium_end = user_data.get("premium_end")
    if not premium_end or datetime.strptime(premium_end, '%Y-%m-%d') < datetime.now():
        await event.reply(
            "🔓 **Este comando es premium.**\n\n"
            "🔑 **Obtén acceso a comandos premium contactando a** @akdios123!",
            parse_mode='markdown'
        )
        logging.info(f"Usuario {username} intentó usar {command} sin acceso premium a las {datetime.now()}")
        return

    # Sugerir uso en grupo
    await event.reply(
        "✨ **Tienes acceso premium!**\n\n"
        "💬 **Te sugerimos usar el bot en el grupo para aprovechar todas las funcionalidades premium, como consultas más rápidas y acceso a más comandos avanzados.**",
        parse_mode='markdown'
    )

    logging.info(f"Usuario {username} con acceso premium intentó usar {command} a las {datetime.now()}")

# Función para manejar todas las respuestas reenviadas y aplicar reemplazos
async def handle_response(event, client):
    original_message_data = original_messages.get(event.message.reply_to_msg_id)
    
    if not original_message_data:
        return

    destination_chat_id = original_message_data['original_chat_id']
    
    # Realizar reemplazos en el mensaje
    message = event.message.text
    replacements = {
        'Cargando....': '🔍 Consultando...',
        'ERROR': '❌ Error',
        '[INFO]': 'ℹ️ Información',
        # Añade más reemplazos según sea necesario
    }
    for old, new in replacements.items():
        message = message.replace(old, new)
    
    # Enviar la respuesta procesada al usuario original
    await client.send_message(destination_chat_id, message)

    logging.info(f"Respuesta reenviada a {original_message_data['original_username']} a las {datetime.now()}")

# Diccionario para almacenar los mensajes originales
original_messages = {}

# Función principal para manejar todos los mensajes privados
async def private_response_handler(event, client):
    text = event.message.text

    if text.startswith('/start'):
        await handle_start(event, client)
    elif text.startswith('/cmds'):
        await handle_cmds(event)
    elif text.startswith(('/tel', '/nm')):  # Comandos free
        command = text.split()[0]
        await handle_free_command(event, command, client)
    elif text.startswith(('/telp', '/dnif')):  # Comandos premium
        command = text.split()[0]
        await handle_premium_command(event, command, client)
    else:
        await event.reply("Comando no reconocido. Usa /cmds para ver los comandos disponibles.", parse_mode='markdown')
        logging.warning(f"Comando no reconocido por {event.sender.username} a las {datetime.now()}")
