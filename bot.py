import os
import re
import asyncio
from telethon import TelegramClient, events
from config2 import makidox_bot_username, bots_usernames, session_name
import config2
import fantasma  # Importamos fantasma.py
import telethon
from PIL import Image
import shutil

client = TelegramClient(config2.session_name, config2.api_id, config2.api_hash)

original_messages = {}
rave_responses = []  # Lista temporal para almacenar respuestas de 'rave'
# Lista de palabras clave que indican que debe reintentarse el envío
palabras_clave_reintentos = ["[⛔] ANTI-SPAM ESPERA", "[⛔] ESPERA ANTES DE REINTENTAR", "Por favor, espere unos segundos", "[ ✖️ ] Jose, debes esperar"]

# Lista de comandos permitidos por cada bot
bot_command_map = {
    'fenix': [
      '/dnifd',
        '/mpfn', '/detenciones', '/antpdf', '/rqpdf', '/denuncias', '/renadespdf',
        '/ant', '/rq', '/sunarp', '/partida', '/dnivir',
        '/dnive', '/licencia', '/agv',  '/bitel',
        '/claro', '/sunedu', '/mine', '/afp',
        '/finan', '/sbs', '/dir', '/sunat', '/ce','/sidtoken','/cve', '/nmve', '/sueldos',
        '/mtc', '/c4w', '/c4t', '/seeker', '/tive','/biv','/tivep','/dni','/dnif','/nm', '/pla', '/migra','/ag','/c4','/antpol', '/tra','/sune','/dnivaz','/dnivam','/cor',
        '/telp','/antpen', '/antjud','/sue','/tel','/fam', '/ag'
    ],
    'Leder': ['/actan', '/actam', '/actad', '/migrapdf', '/fisdet', '/actamdb', '/actaddb', '/fa', '/migrapdfdb', '/agv', '/agvp'],
    'Yape': ['/yape_generate']
}


# Función genérica para procesar el texto de la respuesta, aplicando eliminaciones y reemplazos
def procesar_respuesta_generica(texto_respuesta, comando):
    # Definir los patrones de reemplazo para cada comando
    patrones_reemplazo = {
        '/dnif': {
            'GRADO INSTRUCCION': '[📝] 𝗜𝗡𝗙𝗢\n\n𝗚𝗥𝗔𝗗𝗢 𝗗𝗘 𝗜𝗡𝗦𝗧𝗥𝗨𝗖𝗖𝗜𝗢𝗡',
            'PROVINCIA': '𝗣𝗥𝗢𝗩𝗜𝗡𝗖𝗜𝗔',
            'ESTADO CIVIL': '𝗘𝗦𝗧𝗔𝗗𝗢 𝗖𝗜𝗩𝗜𝗟',
                '[#LEDER_BOT] → RENIEC ONLINE[PREMIUM]': '#PISLLING_DOX_RENIEC\n━━━━━━━━━━━━━━━━━━',

         'DIRECCIÓN': '𝗗𝗜𝗥𝗘𝗖𝗖𝗜𝗢𝗡',

                        '[⚠] Error. Posiblemente el servidor de RENIEC se encuentra caido, porfavor esperar a que se restablezca. Como alternativa puedes usar el respaldo /dnifd.': '[⚒️] 𝗘𝗡 𝗠𝗔𝗡𝗧𝗘𝗡𝗜𝗠𝗜𝗘𝗡𝗧𝗢, 𝗔𝗟𝗧𝗢𝗢𝗢 🗣️',


        },  '/dnifd': {
            'ESTADO CIVIL': '𝗘𝗦𝗧𝗔𝗗𝗢 𝗖𝗜𝗩𝗜𝗟',
            'PROVINCIA': '𝗣𝗥𝗢𝗩𝗜𝗡𝗖𝗜𝗔',

        },
        '/sunarp': {
            'RESULTADOS PROPIEDADES SUNARP': '🏠 | 𝗕𝗜𝗘𝗡𝗘𝗦 𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗔𝗗𝗢𝗦',
            'DOCUMENTO': '𝗗𝗡𝗜',
            'N° PLACA': '𝗠𝗔𝗧𝗥𝗜𝗖𝗨𝗟𝗔',
            'N° PARTIDA': '𝗣𝗔𝗥𝗧𝗜𝗗𝗔',
            'ESTADO': '𝗔𝗖𝗧𝗨𝗔𝗟𝗠𝗘𝗡𝗧𝗘',
            'OFICINA': '𝗢𝗙𝗜𝗖𝗜𝗡𝗔',
            'LIBRO': '𝗔𝗥𝗖𝗛𝗜𝗩𝗔𝗗𝗢',
            'REGISTRO': '𝗜𝗡𝗦𝗖𝗥𝗜𝗧𝗢',
            'ZONA': '𝗔𝗥𝗘𝗔',
            'DIRECCIÓN': '𝗗𝗜𝗥𝗘𝗖𝗖𝗜𝗢𝗡'
        },
         '/claro': {
         'RESULTADOS CLARO' : '☎️ | 𝗕𝗔𝗦𝗘 𝗖𝗟𝗔𝗥𝗢',
         'DNI': '𝗗𝗢𝗖𝗨𝗠𝗘𝗡𝗧𝗢',
         'NUMERO': '𝗡𝗨𝗠𝗘𝗥𝗢',
         'NOMBRES': '𝗡𝗢𝗠𝗕𝗥𝗘',
         'APELLIDOS': '𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢𝗦',
         'ID CLIENTE': '𝗜𝗗',
         'PLAN': '𝗧𝗔𝗥𝗜𝗙𝗔',
         'LINEA': '𝗣𝗟𝗔𝗡',
         'CORREO': '𝗖𝗢𝗥𝗥𝗘𝗢 ',

        },
         '/bitel': {
        'DNI': '𝗗𝗢𝗖𝗨𝗠𝗘𝗡𝗧𝗢',
        'NUMERO': '𝗡𝗨𝗠𝗘𝗥𝗢',
         'NOMBRES': '𝗡𝗢𝗠𝗕𝗥𝗘',
         'APELLIDOS': '𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢𝗦 ',
         'ID CLIENTE': '𝗜𝗗 𝗖𝗟𝗜𝗘𝗡𝗧𝗘 ',
         'CORREO': '𝗖𝗢𝗥𝗥𝗘𝗢 ',

        },
         '/pla': {
        'RESULTADO VEHICULO/PLACA': '🚘 | 𝗥𝗘𝗦𝗨𝗟𝗧𝗔𝗗𝗢 𝗣𝗟𝗔𝗖𝗔',
        'INFORMACIÓN GENERAL': '𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗖𝗜𝗢𝗡 𝗕𝗔𝗦𝗜𝗖𝗔',
         'PLACA': '𝗣𝗟𝗔𝗖𝗔',
         'SERIE': '𝗦𝗘𝗥𝗜𝗘',
         'VIN': '𝗩𝗜𝗡',
         'NRO MOTOR': '𝗠𝗢𝗧𝗢𝗥',
         'MODELO': '𝗠𝗢𝗗𝗘𝗟𝗢',
         'SEDE': '𝗦𝗘𝗗𝗘',
         'COLOR': '𝗖𝗢𝗟𝗢𝗥',
         'ESTADO': '𝗘𝗦𝗧𝗔𝗗𝗢 ',
         '[📍] PROPIETARIOS': '[👥] 𝗣𝗥𝗢𝗣𝗜𝗘𝗧𝗔𝗥𝗜𝗢',
         '-': '→',       
             '🪙 FenixCoins : ♾ - Jose': ' ',
             '🪙 FenixCoins : ♾ - Jose': ' ' ,


        },
            '/nm': {
        'DNI': '𝗗𝗡𝗜',
        '[#LEDER_BOT] → RENIEC NOMBRES [PREMIUM]': '🔍 | 𝗥𝗘𝗦𝗨𝗟𝗧𝗔𝗗𝗢 𝗡𝗢𝗠𝗕𝗥𝗘',
         'APELLIDOS': '𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢𝗦',
         'EDAD': '𝗘𝗗𝗔𝗗'

        },
                '/mpfn': {
        'DOCUMENTO': '𝗗𝗡𝗜',
        'N° CASO': '𝗡° 𝗖𝗔𝗦𝗢',
         'ULTIMA DEPENDENCIA': '𝗨𝗟𝗧𝗜𝗠𝗔 𝗗𝗘𝗣𝗘𝗡𝗗𝗘𝗡𝗖𝗜𝗔',
         'FECHA SITUACION': '𝗙𝗘𝗖𝗛𝗔',
         'TIPO PARTE': '𝗖𝗟𝗔𝗦𝗜𝗙𝗜𝗖𝗔𝗖𝗜𝗢𝗡',
        'ESTADO': '𝗘𝗦𝗧𝗔𝗗𝗢',
        'ESPECIALIDAD': '𝗖𝗟𝗔𝗦𝗜𝗙𝗜𝗖𝗔𝗖𝗜𝗢𝗡',
        'DELITO': '𝗗𝗘𝗟𝗜𝗧𝗢',       

         'RESULTADOS FISCALIA': '⚖ | 𝗥𝗘𝗦𝗨𝗟𝗧𝗔𝗗𝗢 𝗠𝗣𝗙𝗡',


        },
                '/bitel': {
        'DOCUMENTO': '𝗗𝗡𝗜',
        'NUMERO': '𝗡𝗨𝗠𝗘𝗥𝗢',
         'TIPO': '𝗖𝗟𝗔𝗦𝗜𝗙𝗜𝗖𝗔𝗖𝗜𝗢𝗡',
         'PLAN': '𝗣𝗟𝗔𝗡',
         'TITULAR': '𝗧𝗜𝗧𝗨𝗟𝗔𝗥',
        'FECHA ACTIVACIÓN': '𝗙𝗘𝗖𝗛𝗔 𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗢',
        'RESULTADOS BITEL': '🟡 | 𝗥𝗘𝗦𝗨𝗟𝗧𝗔𝗗𝗢 𝗕𝗜𝗧𝗘𝗟',

        },
                '/cor': {
        'DOCUMENTO': '𝗗𝗡𝗜',
        'CORREO': '𝗖𝗢𝗥𝗥𝗘𝗢',
         'FUENTE': '𝗙𝗨𝗘𝗡𝗧𝗘',
         'FECHA': '𝗙𝗘𝗖𝗛𝗔',
        'RESULTADOS CORREOS': '📩 | 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗖𝗜𝗢𝗡 𝗖𝗢𝗥𝗥𝗘𝗢',
        'CORREO': '𝗖𝗢𝗥𝗥𝗘𝗢 ',


        } ,     '/sueldos': {
        'DNI': '𝗗𝗢𝗖𝗨𝗠𝗘𝗡𝗧𝗢',
        'RUC': '𝗥𝗨𝗖',
        'SITUACION': '𝗘𝗦𝗧𝗔𝗗𝗢',
        'EMPRESA': '𝗘𝗡𝗧𝗜𝗗𝗔𝗗',
        'SUELDO': '𝗦𝗔𝗟𝗔𝗥𝗜𝗢',
        'PERIODO': '𝗖𝗨𝗥𝗦𝗢 𝗘𝗡',
        'RESULTADOS SUELDOS': '💸 | 𝗛𝗜𝗦𝗧𝗢𝗥𝗜𝗔𝗟 𝗦𝗔𝗟𝗔𝗥𝗜𝗔𝗟',   

        
    },            '/tra': {
        'DNI': '𝗗𝗢𝗖𝗨𝗠𝗘𝗡𝗧𝗢',
        'RUC': '𝗥𝗨𝗖',
        'SITUACION': '𝗘𝗦𝗧𝗔𝗗𝗢',
        'EMPRESA': '𝗘𝗡𝗧𝗜𝗗𝗔𝗗',
        'PERIODO': '𝗖𝗨𝗥𝗦𝗢 𝗘𝗡',     
        'RESULTADOS TRABAJOS': '💼 | 𝗛𝗜𝗦𝗧𝗢𝗥𝗜𝗔𝗟 𝗖𝗛𝗔𝗠𝗕𝗔𝗦',

        
    } ,  '/telp': {
        'DNI': '𝗗𝗡𝗜',
         'TIPO': '𝗖𝗟𝗔𝗦𝗜𝗙𝗜𝗖𝗔𝗖𝗜𝗢𝗡',
         'PLAN': '𝗧𝗔𝗥𝗜𝗙𝗔',
         'TITULAR': '𝗧𝗜𝗧𝗨𝗟𝗔𝗥',
                  'PERIODO': '𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗢',

        } ,  '/tel': {
        'DNI': '𝗗𝗡𝗜',
         'TIPO': '𝗖𝗟𝗔𝗦𝗜𝗙𝗜𝗖𝗔𝗖𝗜𝗢𝗡',
         'PLAN': '𝗣𝗟𝗔𝗡',
         'TITULAR': '𝗧𝗜𝗧𝗨𝗟𝗔𝗥',
                  'PERIODO': '𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗢',


        },
            '/migra': {
        'FECHA MOVIMIENTO': '𝗙𝗘𝗖𝗛𝗔 𝗠𝗢𝗩.',
        'NRO DOCUMENTO': '𝗡𝗥𝗢 𝗗𝗢𝗖𝗨𝗠𝗘𝗡𝗧𝗢',
         'PROCEDENCIA/DESTINO': '𝗣𝗔𝗥𝗧𝗜𝗗𝗔/𝗗𝗘𝗦𝗧𝗜𝗡𝗢',
         'TIPO DOCUMENTO': '𝗧𝗜𝗣𝗢 𝗗𝗘 𝗗𝗢𝗖𝗨. ',
         'TIPO MOVIMIENTO': '𝗧𝗜𝗣𝗢 𝗠𝗢𝗩𝗜𝗠𝗜𝗘𝗡𝗧𝗢'

        }
        # Puedes agregar más comandos aquí
        # Puedes agregar más comandos aquí
    }
 # Aplicar el patrón de eliminación específico de 'ACTAS REGISTRADAS' solo para ciertos comandos
    if comando in ['/dnif', '/dnid']:
        patron_eliminar = r'ACTAS / CERTIFICADOS.*'
        texto_respuesta = re.sub(patron_eliminar, '', texto_respuesta, flags=re.DOTALL)
    # Aplicar los reemplazos correspondientes al comando usando expresiones regulares
    if comando in patrones_reemplazo:
        for patron, reemplazo in patrones_reemplazo[comando].items():
            texto_respuesta = re.sub(patron, reemplazo, texto_respuesta)

    # Ajustes genéricos para eliminar patrones no deseados
    texto_respuesta = re.sub(r'\(\s*\d+\s*\)\s*\[\s*\d+/\s*\d+\s*\]', '', texto_respuesta)
    texto_respuesta = re.sub(r'\(.*?\]\s*', '', texto_respuesta)
    texto_respuesta = re.sub(r'\(\d+\)', '', texto_respuesta)

    return texto_respuesta

async def handle_command(event):
    sender = await event.get_sender()
    username = sender.username
    message = event.message.message
    command = message.split()[0]
    command_args = ' '.join(message.split()[1:])

    print(f"handle_command: Usuario={username}, Comando={command}")

    if command == '/rhf':
        command = '/dnif'
        message = f"{command} {command_args}"
        original_messages[event.message.id] = {
            'original_chat_id': event.chat_id,
            'original_user_id': sender.id,
            'command': command,
            'send_only_images': True,
            'retries': 0
        }
    elif command == '/dni':
        command = '/dnif'
        message = f"{command} {command_args}"
        original_messages[event.message.id] = {
            'original_chat_id': event.chat_id,
            'original_user_id': sender.id,
            'command': command,
            'send_only_text': True,
            'retries': 0
        }
    else:
        original_messages[event.message.id] = {
            'original_chat_id': event.chat_id,
            'original_user_id': sender.id,
            'command': command,
            'send_only_images': False,
            'send_only_text': False,
            'retries': 0
        }

    target_bot = None
    for bot, commands in bot_command_map.items():
        if command in commands:
            target_bot = bot
            break

    if not target_bot:
        return

    target_bot_username = bots_usernames.get(target_bot)

    if not target_bot_username:
        await event.reply("❌ No se encontró el bot para este comando.", parse_mode='markdown')
        return

    try:
        entity = await client.get_input_entity(target_bot_username)
        sent_message = await client.send_message(entity, message)
        original_messages[sent_message.id] = original_messages[event.message.id]
        original_messages[sent_message.id]['original_id'] = event.message.id
    except Exception as e:
        print(f"Error enviando el mensaje: {e}")
async def handle_images(event, images):
    for image in images: 
        await event.reply(file=image)
import shutil

@client.on(events.NewMessage(from_users=list(bots_usernames.values())))
async def forward_response(event):
    """
    Procesa las respuestas de los bots y maneja las condiciones de envío.
    """
    # Captura respuestas rápidas de 'rave'
    if event.sender_id == bots_usernames['Leder']:
        global rave_responses
        rave_responses.append(event.message)

    # Obtener los datos del mensaje original
    original_message_data = original_messages.get(event.message.reply_to_msg_id)
    if not original_message_data:
        return

    destination_chat_id = original_message_data['original_chat_id']
    original_id = original_message_data['original_id']
    command_used = original_message_data['command'].split()[0]

    # Verificar si el mensaje debe enviar solo texto
    if original_message_data.get('send_only_text', False):
        texto_procesado = procesar_respuesta_generica(event.message.text, command_used)
        await client.send_message(destination_chat_id, texto_procesado, reply_to=original_id)
        print(f"Respuesta de solo texto enviada para {command_used}.")
        return

    # Verificar si debe enviar solo imágenes
    enviar_solo_imagenes = original_message_data.get('send_only_images', False)

    try:
        # Manejo de reintentos si se detectan mensajes de anti-spam
        if any(palabra in event.message.text for palabra in palabras_clave_reintentos):
            original_message_data['retries'] += 1
            if original_message_data['retries'] <= 2:
                await asyncio.sleep(5)
                print("Reintentando enviar el comando...")
                try:
                    await client.send_message(event.sender_id, original_message_data['command'])
                except Exception as e:
                    print(f"Error reenviando el comando: {e}")
            else:
                await client.send_message(destination_chat_id, "⚠️ Se ha alcanzado el máximo de reintentos.", reply_to=original_id)
            return

        # Manejo de mensajes con "Cargando..."
        if "Cargando...." in event.message.text:
            await client.send_message(destination_chat_id, event.message.text, reply_to=original_id)
            print(f"Texto enviado sin imagen: {event.message.text}")
            return

        # Procesar comandos específicos
        if command_used in ['/dnif', '/dni', '/sunarp', '/telp', '/tel', '/tra', '/sueldos', '/denuncias', '/bitel', '/claro', '/nm', '/pla', '/ag', '/mpfn', '/co']:
            texto_procesado = procesar_respuesta_generica(event.message.text, command_used) if not enviar_solo_imagenes else ""

            if event.message.media:
                media_path = await event.message.download_media()

                if enviar_solo_imagenes:
                    
                    await client.send_file(destination_chat_id, media_path, reply_to=original_id)
                    print(f"Solo imagen enviada para {command_used}: {media_path}")
                else:
                    await client.send_message(destination_chat_id, texto_procesado, reply_to=original_id)
                    await client.send_file(destination_chat_id, media_path, reply_to=original_id)
                    print(f"Texto e imagen enviados para {command_used}: {media_path}")

                if os.path.exists(media_path):
                    os.remove(media_path)
                    print(f"Archivo eliminado: {media_path}")

            else:
                await client.send_message(destination_chat_id, texto_procesado, reply_to=original_id)
                print(f"Solo texto enviado para {command_used}.")

        elif event.message.media:
            # Manejo de archivos PDF o imágenes
            if event.message.file and event.message.file.mime_type == 'application/pdf':
                pdf_path = await event.message.download_media()
                pdf_procesado_path = fantasma.procesar_pdf_y_eliminar_logo(pdf_path)

                try:
                    imagen_portada_path = os.path.join(os.getcwd(), "portada.png")
                    if os.path.isfile(imagen_portada_path):
                        with Image.open(imagen_portada_path) as img:
                            img.thumbnail((90, 90))
                            img.save(imagen_portada_path)

                        await client.send_file(destination_chat_id, file=pdf_procesado_path, thumb=imagen_portada_path, reply_to=original_id)
                        print(f"PDF enviado con portada: {pdf_procesado_path}")

                    else:
                        await client.send_file(destination_chat_id, file=pdf_procesado_path, reply_to=original_id)
                        print(f"PDF enviado sin portada: {pdf_procesado_path}")

                finally:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                        print(f"Archivo PDF original eliminado: {pdf_path}")
                    if os.path.exists(pdf_procesado_path):
                        os.remove(pdf_procesado_path)
                        print(f"Archivo PDF procesado eliminado: {pdf_procesado_path}")

            else:
                media_path = await event.message.download_media()
                await client.send_file(destination_chat_id, media_path, reply_to=original_id)
                print(f"Media enviada: {media_path}")
                if os.path.exists(media_path):
                    os.remove(media_path)

        else:
            await client.send_message(destination_chat_id, event.message.text, reply_to=original_id)
            print(f"Solo texto enviado al usuario.")

    except telethon.errors.rpcerrorlist.MessageDeleteForbiddenError:
        print("El mensaje fue eliminado y no se pudo reenviar.")
    except Exception as e:
        print(f"Error reenviando el mensaje: {e}")
# Diccionario para rastrear comandos pendientes de /yape_generate
pending_yape_requests = {}

yape_bot_username = 'JupyterPeBot'  # Nombre de usuario del bot Yape

@client.on(events.NewMessage(pattern='/yape_generate'))
async def handle_yape_generate(event):
    """
    Maneja el comando /yape_generate, enviándolo al bot Yape y rastreando la respuesta.
    """
    # Obtener el contenido del comando
    command_args = event.message.text.split(maxsplit=1)
    if len(command_args) < 2:
        await event.reply("Uso incorrecto. Ejemplo: /yape_generate 500|Josue A. Rabano C.|999")
        return

    query = command_args[1]

    # Enviar el mensaje al bot Yape
    await client.send_message(yape_bot_username, query)

    # Registrar el mensaje pendiente para capturar la respuesta
    pending_yape_requests[event.message.id] = {
        'original_event': event,
        'responses': []
    }

@client.on(events.NewMessage(from_users=yape_bot_username))
async def handle_yape_response(event):
    """
    Maneja las respuestas provenientes del bot Yape y las reenvía como respuesta al usuario original.
    """
    # Buscar si hay algún comando pendiente
    for original_message_id, request_data in list(pending_yape_requests.items()):
        if len(request_data['responses']) < 2:  # Máximo 2 mensajes por respuesta
            # Agregar el mensaje a las respuestas rastreadas
            request_data['responses'].append(event.message)

            # Responder al usuario original como respuesta directa al comando
            original_event = request_data['original_event']
            await original_event.reply(event.message.message, file=event.message.media)

        # Si ya se capturaron 2 mensajes, eliminar el registro pendiente
        if len(request_data['responses']) >= 2:
            del pending_yape_requests[original_message_id]

@client.on(events.MessageEdited)
async def handle_edited_message(event):
    # Captura ediciones de mensajes de 'rave'
    if event.sender_id == bots_usernames['Leder']:
        global rave_responses
        rave_responses.append(event.message)  # Tratar la edición como si fuera un nuevo mensaje

        print(f"Mensaje de 'Leder' editado y capturado: {event.message.text}")

@client.on(events.MessageDeleted)
async def handle_deleted_message(event):
    for deleted_id in event.deleted_ids:
        original_message_data = original_messages.get(deleted_id)

        if original_message_data:
            try:
                await client.delete_messages(original_message_data['original_chat_id'], original_message_data['original_id'])
                print(f"Mensaje eliminado: {original_message_data['original_id']}")
            except Exception as e:
                print(f"Error eliminando el mensaje: {e}")

@client.on(events.NewMessage(incoming=True, from_users=makidox_bot_username))
async def handle_private_message(event):
    await handle_command(event)

async def main():
    await client.start()
    print("Bot iniciado. Esperando comandos...")

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
