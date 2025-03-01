import re
import json
from telethon import TelegramClient, events, Button
from telethon.errors import PeerIdInvalidError, RPCError, UsernameNotOccupiedError
from telethon.tl.types import DocumentAttributeFilename, InputMediaUploadedDocument
from collections import defaultdict
import os
from datetime import datetime, timedelta
import asyncio
from commando_id import iniciar_manejador_id
from calificar import iniciar_comando_calificar, iniciar_comando_ver_calificacion
from donar import iniciar_comando_donar  # Importar el comando /donar desde el archivo donar.py
from fake import registrar_comando_fake
from datetime import datetime, timedelta
from collections import defaultdict
from precios import verificar_acceso, get_user_data, reducir_creditos
from flask import Flask
import threading

import vernum  # Importa el archivo vernum.py

# Lista de comandos que requieren enviar la respuesta al privado
private_response_commands = ['/comando1', '/comando2'
                             ]  # Reemplaza con los comandos que quieras

# Configuraciones del antispam
ANTISPAM_SHORT = timedelta(seconds=10)
ANTISPAM_LONG = timedelta(seconds=15)
COMMAND_LIMIT = 8  # Límite de comandos para activar el antispam largo

# Diccionarios para registrar el tiempo del último comando y el conteo de comandos
last_command_timestamps = defaultdict(lambda: datetime.min)
command_count = defaultdict(int)

api_id = '24128308'
api_hash = 'e1d006e1aede7e1159b55148232780d7'
# Reemplaza con tus credenciales de API de Telegram
bot_token = '7891374452:AAHzeAEWcY_ub2Sa0WbPi0O_kkcqmNOQ9b4'
leo_vidal_username = 'josepapu14'
notification_chat_id = -1002463106762  # Elimina las comillas para que sea un número entero

user_data_file = 'user_data.json'
active_groups_file = 'active_groups.json'
pending_responses = defaultdict(list)
ID_FILE = 'id.json'

command_translation = {
    '/antpenver': '/antpenver',
    '/antpolver': '/antpolver',
    '/antjudver': '/antjudver',
    '/tive': '/tive',
    '/dnive2': '/dniv',
    '/dni': '/dni',
    '/fk': '/fake',
    '/check': '/chk',
    '/dnifb': '/dnifd',
    '/nm': '/nm',
    '/actan': '/actan',
    '/actam2': '/actamdb',
    '/actad2': '/actaddb',
    '/actan': '/actan',
    '/fisdet': '/fisdet',
    '/c4f': '/fa',
    '/yape': '/yape_generate',
    '/actam': '/actam',
    '/actad': '/actad',
    '/mpfn': '/mpfn',
    '/arrestos': '/detenciones',
    '/antpdf': '/antpdf',
    '/rqpdf': '/rqpdf',
    '/renadespdf': '/renadespdf',
    '/ant': '/ant',
    '/rq': '/rq',
    '/bienes': '/sunarp',
    '/placa': '/pla',
    '/partida': '/partida',
    '/dniv': '/dnivir',
    '/dnie': '/dnivel',
    '/licencia': '/licencia',
    '/migrapdf': '/migrapdf',
    '/fono': '/tel',
    '/telp': '/telp',
    '/pnp': '/sidtoken',
    '/bitx': '/bitel',
    '/clax': '/claro',
    '/bolinf': '/biv',
    '/plantive': '/tivep',
    '/dnivz': '/dnivaz',
    '/dnivm': '/dnivam',
    '/arbol': '/ag',
    '/chamba': '/tra',
    '/titulos': '/sune',
    '/mine': '/mine',
    '/afp': '/afp',
    '/dnif': '/rhf',
    '/finan': '/finan',
    '/doxcorreo': '/co',
    '/dir': '/dir',
    '/sunat': '/sunat',
    '/ce': '/ce',
    '/cve': '/cve',
    '/nmve': '/nmve',
    '/salario': '/sue',
    '/migra': '/migra',
    '/familia': '/fam',
    '/mtc': '/mtc',
    '/c4': '/c4',
    '/c4b': '/c4w',
    '/migrapdf2': '/migrapdfdb',
    '/agvx': '/agv',
    '/agv10': '/agvp',
    '/c4t': '/c4t',
    '/antpol': '/antpol',
    '/antpen': '/antpen',
    '/antjud': '/antjud',
}

non_forward_commands = [
    '/cmds', '/help', '/status', '/addprem', '/unprem', '/info', '/register',
    '/buy', '/blocklist', '/addowner', '/addseller', '/bangrupo', '/banpriv',
    '/banglobal', '/unbangrupo', '/unbanpriv', '/unbanglobal', '/me', '/rol',
    '/addid', '/ad', '/start'
]
user_command_count = defaultdict(int)
max_free_commands = 4

command_costs = {
    '/dnif': 2,
    '/dnifb': 2,
    '/nm': 2,
    '/actan': 13,
    '/dni': 2,
    '/c4f': 2,
    '/fisdet': 15,
    '/actam': 13,
    '/actad': 13,
    '/mpfn': 6,
    '/arrestos': 5,
    '/antpdf': 3,
    '/rqpdf': 5,
    '/renadespdf': 8,
    '/ant': 4,
    '/rq': 3,
    '/bienes': 4,
    '/placa': 3,
    '/partida': 3,
    '/dnivir': 4,
    '/dnielec': 4,
    '/licencia': 4,
    '/migrapdf': 8,
    '/fono': 2,
    '/dnive2': 2,
    '/dni': 2,
    '/familia': 4,
    '/dnivm': 4,
    '/dnivz': 4,
    '/telp': 5,
    '/bitx': 4,
    '/clax': 4,
    '/arbol': 3,
    '/chamba': 3,
    '/titulos': 3,
    '/mine': 4,
    '/afp': 3,
    '/finan': 4,
    '/doxcorreo': 4,
    '/dir': 4,
    '/sunat': 3,
    '/ce': 1,
    '/cve': 1,
    '/nmve': 1,
    '/salario': 4,
    '/yape': 2,
    '/rhf': 4,
    '/migra': 6,
    '/mtc': 2,
    '/c4': 3,
    '/c4b': 4,
    '/c4t': 3,
    '/antpol': 3,
    '/antpen': 3,
    '/antjud': 3,
    '/antpolver': 2,
    '/antpenver': 2,
    '/antjudver': 2,
    '/tive': 12,
    '/chk': 0,
    '/fake': 1,
}

blocked_data = {
    "names": ["andy ruben ravines sanchez"],
    "numbers": ["927904737"],
    "dni": ["61769516"]
}
banpriv = False  # Variable global para controlar el estado de banpriv
owner_username = 'AKdios'
owners = [owner_username, 'yuta_faster', 'AKdios', 'OKARUN_7', 'reigenpe']
sellers = [owner_username, 'The_Goa7', 'LuckLP']

global_ban_status = {
    "group_ban": False,
    "private_ban": False,
    "global_ban": False
}

client = TelegramClient('bot_session', api_id, api_hash)
commands = {
    'RENIEC': [
        ("➥ 𝗖𝟰 𝗔𝗭𝗨𝗟",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /c4 51234789"),
        ("➥ 𝗖𝟰 𝗜𝗡𝗦𝗖𝗥𝗜𝗣𝗖𝗜𝗢𝗡",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /c4t 51234789"),
        ("➥ 𝗖𝟰 𝗕𝗟𝗔𝗡𝗖𝗢",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /c4b 51234789"),
        ("➥ 𝗗𝗔𝗧𝗢𝗦 𝗘𝗡 𝗧𝗘𝗫𝗧𝗢",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /dni 61234578"),
        ("➥ 𝗙𝗢𝗧𝗢, 𝗙𝗜𝗥𝗠𝗔 𝗬 𝗛𝗨𝗘𝗟𝗟𝗔𝗦",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /dnif 61234578"),
        ("➥ 𝗕𝗨𝗦𝗖𝗔𝗥 𝗡𝗢𝗠𝗕𝗥𝗘𝗦",
        "⌞ Estado: ACTIVO\n⌞ Costo: 2\n⌞ Uso: /nm Omar|Carrillo|Cruz"),
        ("➥ 𝗔𝗖𝗧𝗔 𝗡𝗔𝗖𝗜𝗠𝗜𝗘𝗡𝗧𝗢",
        "⌞ Estado: OFF\n⌞ Costo: 13\n⌞ Uso: /actan 93123456"),
        ("➥ 𝗔𝗖𝗧𝗔 𝗠𝗔𝗧𝗥𝗜𝗠𝗢𝗡𝗜𝗢",
        "⌞ Estado: OFF\n⌞ Costo: 13\n⌞ Uso: /actam 34567812"),
        ("➥ 𝗔𝗖𝗧𝗔 𝗗𝗘𝗙𝗨𝗡𝗖𝗜𝗢𝗡",
        "⌞ Estado: OFF\n⌞ Costo: 13\n⌞ Uso: /actad 43567218"),
    ],
    'DELITOS': [
        ("➥ 𝗔𝗡𝗧. 𝗣𝗗𝗙",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /antpdf 52413768"),
        ("➥ 𝗥𝗤 𝗣𝗗𝗙",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /rqpdf 15342689"),
        ("➥ 𝗥𝗘𝗡𝗔𝗗𝗘𝗦 𝗣𝗗𝗙",
        "⌞ Estado: ACTIVO\n⌞ Costo: 8\n⌞ Uso: /renadespdf 81234567"),
        ("➥ 𝗔𝗡𝗧𝗘𝗖𝗘𝗗𝗘𝗡𝗧𝗘𝗦",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /antpdf 23456789"),
    ],
    'SUNARP': [
        ("➥ 𝗦𝗨𝗡𝗔𝗥𝗣",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /bienes 97812345"),
        ("➥ 𝗣𝗟𝗔𝗖𝗔",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /placa XYZ123 o 91234567"),
        ("➥ 𝗣𝗔𝗥𝗧𝗜𝗗𝗔 𝗦𝗨𝗡𝗔𝗥𝗣",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /partida 56781234"),
    ],
    'GENERADORES': [
        ("➥ 𝗗𝗡𝗜 𝗔𝗭𝗨𝗟/𝗔𝗠𝗔𝗥𝗜𝗟𝗟𝗢",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /dniv 74561238"),
        ("➥ 𝗗𝗡𝗜 𝗘𝗟𝗘𝗖𝗧𝗥𝗢𝗡𝗜𝗖𝗢",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /dnie 25617483"),
        ("➥ 𝗟𝗜𝗖. 𝗗𝗘 𝗖𝗢𝗡𝗗𝗨𝗖𝗜𝗥 𝗘𝗟𝗘𝗖.",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /licencia 67235841"),
        ("➥ 𝗠𝗢𝗩𝗜𝗠𝗜𝗘𝗡𝗧𝗢𝗦 𝗠𝗜𝗚𝗥𝗔𝗧𝗢𝗥𝗜𝗢𝗦",
        "⌞ Estado: ACTIVO\n⌞ Costo: 8\n⌞ Uso: /migrapdf 38472615"),
        ("➥ 𝗔𝗡𝗧𝗘𝗖𝗘𝗗𝗘𝗡𝗧𝗘𝗦 𝗣𝗘𝗡𝗔𝗟𝗘𝗦 𝗣𝗗𝗙",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /antpen 52413768"),
        ("➥ 𝗔𝗡𝗧𝗘𝗖𝗘𝗗𝗘𝗡𝗧𝗘𝗦 𝗣𝗢𝗟𝗜𝗖𝗜𝗔𝗟𝗘𝗦 𝗣𝗗𝗙",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /antpol 63456789"),
        ("➥ 𝗔𝗡𝗧𝗘𝗖𝗘𝗗𝗘𝗡𝗧𝗘𝗦 𝗝𝗨𝗗𝗜𝗖𝗜𝗔𝗟𝗘𝗦 𝗣𝗗𝗙",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /antjud 74567890"),
    ],
    'EXTRA': [
        ("➥ 𝗦𝗔𝗟𝗔𝗥𝗜𝗢",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /salario 65432198"),
        ("➥ 𝗧𝗘𝗟𝗘𝗙𝗢𝗡𝗢𝗦",
        "⌞ Estado: ACTIVO\n⌞ Costo: 2\n⌞ Uso: /fono 43219876, /fono 87654321"
         ),
        ("➥ 𝗧𝗘𝗟𝗘𝗙𝗢𝗡𝗢𝗦",
        "⌞ Estado: ACTIVO\n⌞ Costo: 5\n⌞ Uso: /telp 64321890, /telp 987654321"
         ),
        ("➥ 𝗧𝗘𝗟. 𝗕𝗜𝗧𝗘𝗟",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /bitx 76329184"),
        ("➥ 𝗧𝗘𝗟. 𝗖𝗟𝗔𝗥𝗢",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /clax 92183647"),
        ("➥ 𝗔𝗥𝗕. 𝗚𝗘𝗡𝗘𝗔𝗟𝗢𝗚𝗜𝗖𝗢",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /arbol 86372415"),
        ("➥ 𝗡𝗢𝗧𝗔𝗦", 
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /notas 56723489"),
        ("➥ 𝗧𝗜𝗧𝗨𝗟𝗢𝗦 𝗨.",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /titulos 23457816"),
        ("➥ 𝗖𝗛𝗔𝗠𝗕𝗔𝗦",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /chamba 52147836"),
        ("➥ 𝗧.𝗜.𝗩.𝗘.",
        "⌞ Estado: ACTIVO\n⌞ Costo: 12\n⌞ Uso: /tive XYZ123"),
        ("➥ 𝗛𝗜𝗦𝗧. 𝗗𝗜𝗥𝗘𝗖𝗖𝗜𝗢𝗡𝗘𝗦",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /dir 94837216"),
        ("➥ 𝗗𝗢𝗫𝗘𝗔𝗥 𝗖𝗢𝗥𝗥𝗘𝗢",
        "⌞ Estado: ACTIVO\n⌞ Costo: 4\n⌞ Uso: /doxcorreo 12348976"),
        ("➥ 𝗦𝗨𝗡𝗔𝗧",
        "⌞ Estado: ACTIVO\n⌞ Costo: 3\n⌞ Uso: /sunat 39182756"),
        ("➥ 𝗖𝗔𝗥𝗡𝗘𝗧 𝗗𝗘 𝗘𝗫𝗧𝗥𝗔𝗡𝗝𝗘𝗥𝗜𝗔",
        "⌞ Estado: ACTIVO\n⌞ Costo: 1\n⌞ Uso: /ce 789123456"),
        ("➥ 𝗖𝗘. 𝗩𝗘𝗡𝗘𝗖𝗔",
        "⌞ Estado: ACTIVO\n⌞ Costo: 1\n⌞ Uso: /cve 00001 o /cve 32897112"),
        ("➥ 𝗡𝗢𝗠𝗕𝗥𝗘𝗦 𝗩𝗘𝗡𝗘𝗖𝗢",
        "⌞ Estado: ACTIVO\n⌞ Costo: 1\n⌞ Uso: /nmve OMAR|CARRILLO|CRUZ"),
    ]
}
# Ruta de la imagen del menú principal
menu_image = 'cmds.png'


# Función para mostrar el menú principal o regresar a él, editando el mensaje existente
async def show_menu(chat_id, user_id, event=None):
    if event:
        # Editar el mensaje actual
        await event.edit(
            file=menu_image,  # Imagen del menú principal
            text=
            ("🧩 **𝗕𝗜𝗘𝗡𝗩𝗘𝗡𝗜𝗗𝗢 𝗔 𝗟𝗔 𝗦𝗘𝗖𝗖𝗜𝗢𝗡 𝗗𝗘 𝗖𝗢𝗠𝗔𝗡𝗗𝗢𝗦 𝗗𝗘 #ℙ𝕀𝕊𝕃𝕃𝕀ℕ𝔾_𝔻𝕆𝕏.** \n\n"
             "⬐ **⬇️ 𝗦𝗘𝗟𝗘𝗖𝗖𝗜𝗢𝗡𝗔 𝗨𝗡𝗔 𝗢𝗣𝗖𝗜𝗢𝗡 ⬇️** ⬎"),
            buttons=[
                [
                    Button.inline("📂 𝗥𝗘𝗡𝗜𝗘𝗖", f"RENIEC_0_{user_id}"),
                    Button.inline("⚖️ 𝗗𝗘𝗟𝗜𝗧𝗢𝗦", f"DELITOS_0_{user_id}")
                ],
                [
                    Button.inline("🏛️ 𝗦𝗨𝗡𝗔𝗥𝗣", f"SUNARP_0_{user_id}"),
                    Button.inline("📃 𝗚𝗘𝗡𝗘𝗥𝗔𝗗𝗢𝗥𝗘𝗦", f"GENERADORES_0_{user_id}")
                ], [Button.inline("📦 𝗘𝗫𝗧𝗥𝗔", f"EXTRA_0_{user_id}")],
                [Button.inline("🏠 𝗠𝗘𝗡𝗨 𝗣𝗥𝗜𝗡𝗖𝗜𝗣𝗔𝗟", f"main_menu_{user_id}")]
            ])
    else:
        # Enviar un nuevo mensaje solo si no se proporciona un evento para editar
        await client.send_file(
            chat_id,
            menu_image,  # Imagen del menú principal
            caption=
            ("🧩 **𝗕𝗜𝗘𝗡𝗩𝗘𝗡𝗜𝗗𝗢 𝗔 𝗟𝗔 𝗦𝗘𝗖𝗖𝗜𝗢𝗡 𝗗𝗘 𝗖𝗢𝗠𝗔𝗡𝗗𝗢𝗦 𝗗𝗘 #ℙ𝕀𝕊𝕃𝕃𝕀ℕ𝔾_𝔻𝕆𝕏.** \n\n"
             "⬐ **⬇️ 𝗦𝗘𝗟𝗘𝗖𝗖𝗜𝗢𝗡𝗔 𝗨𝗡𝗔 𝗢𝗣𝗖𝗜𝗢𝗡 ⬇️** ⬎"),
            buttons=[
                [
                    Button.inline("📂 𝗥𝗘𝗡𝗜𝗘𝗖", f"RENIEC_0_{user_id}"),
                    Button.inline("⚖️ 𝗗𝗘𝗟𝗜𝗧𝗢𝗦", f"DELITOS_0_{user_id}")
                ],
                [
                    Button.inline("🏛️ 𝗦𝗨𝗡𝗔𝗥𝗣", f"SUNARP_0_{user_id}"),
                    Button.inline("📃 𝗚𝗘𝗡𝗘𝗥𝗔𝗗𝗢𝗥𝗘𝗦", f"GENERADORES_0_{user_id}")
                ],
                [Button.inline("📦 𝗘𝗫𝗧𝗥𝗔", f"EXTRA_0_{user_id}")],
            ])


# Función para crear botones de paginación con el user_id
def create_pagination_buttons(section, page, user_id):
    buttons = []
    total_commands = len(commands[section])

    # Botón "Anterior" si no estamos en la primera página
    if page > 0:
        buttons.append(
            Button.inline("⬅️ 𝗔𝗡𝗧𝗘𝗥𝗜𝗢𝗥", f"{section}_{page-1}_{user_id}"))

    # Botón "Menú Principal"
    buttons.append(Button.inline("🏠 𝗠𝗘𝗡𝗨 𝗣𝗥𝗜𝗡𝗖𝗜𝗣𝗔𝗟", f"main_menu"))

    # Botón "Siguiente" si hay más comandos después de la página actual
    if (page + 1) * 6 < total_commands:
        buttons.append(
            Button.inline("➡️ 𝗦𝗜𝗚𝗨𝗜𝗘𝗡𝗧𝗘", f"{section}_{page+1}_{user_id}"))

    return buttons


# Manejador de comandos especiales como /cmds
@client.on(events.NewMessage(pattern='/cmds'))
async def cmds(event):
    sender = await event.get_sender()
    await show_menu(
        event.chat_id, sender.id
    )  # Llamar a la función para mostrar el menú principal con el ID del usuario


# Manejar las interacciones con los botones
@client.on(events.CallbackQuery)
async def callback_handler(event):
    query_data = event.data.decode('utf-8')
    user_id = event.sender_id  # ID del usuario que interactúa

    # Dividir los datos de la consulta
    parts = query_data.split("_")

    # Manejo especial para el botón "Menú Principal"
    if query_data == "main_menu":
        await show_menu(event.chat_id, user_id, event=event
                        )  # Editar el mensaje para volver al menú principal
        return

    if len(parts) < 3:
        await event.answer('Interacción no reconocida.', alert=True)
        return

    section = parts[0]
    action_or_page = parts[1]
    command_user_id = int(parts[2])  # ID del usuario que ejecutó /cmds

    if command_user_id != user_id:
        # Evitar que otros usuarios interactúen con los botones
        await event.answer("No puedes interactuar con este menú.", alert=True)
        return

    # Procesar la navegación del menú o la paginación
    try:
        if section in commands:
            page = int(action_or_page)

            # Calcular los índices de inicio y fin para los comandos a mostrar
            start = page * 6
            end = min(start + 6, len(commands[section]))

            # Obtener los comandos correspondientes a la página actual
            commands_to_show = commands[section][start:end]

            if commands_to_show:  # Verificar que haya comandos para mostrar
                # Generar el texto de los comandos con estilo mejorado
                text = "\n\n".join(
                    [f" {cmd[0]}\n {cmd[1]}" for cmd in commands_to_show])

                # Crear botones de paginación
                buttons = create_pagination_buttons(section, page, user_id)

                # Editar el mensaje actual con el nuevo texto, imagen y botones
                await event.edit(file=menu_image, text=text, buttons=buttons)
            else:
                await event.answer(
                    'No hay comandos disponibles en esta sección.', alert=True)

        else:
            await event.answer('Sección no reconocida.', alert=True)

    except Exception as e:
        print(f"Exception: {e}")
        await event.answer(f'Ocurrió un error: {str(e)}', alert=True)


@client.on(events.NewMessage(pattern='/vernum'))
async def vernum_command(event):
    sender = await event.get_sender()
    username = sender.username

    # Obtener los datos del usuario en tiempo real desde el archivo JSON
    user_data = get_user_data(username)

    # Verificar si el usuario tiene acceso basado en el plan o créditos
    precio_comando = 1  # Asignamos el precio del comando (puede cambiar dependiendo del comando)
    acceso, motivo = verificar_acceso(user_data, precio_comando)

    if not acceso:
        # Si el usuario no tiene acceso, enviar el mensaje correspondiente
        await event.reply(motivo, parse_mode='markdown')
        return

    # Verificar si el número de teléfono fue proporcionado correctamente
    message_text = event.message.message.strip()
    parts = message_text.split()

    if len(parts) != 2:
        await event.reply(
            "Por favor, usa el formato correcto: `/vernum <número_de_teléfono>`",
            parse_mode='markdown')
        return

    numero_telefono = parts[1]

    # Validar el número de teléfono (9 dígitos y no debe empezar con 0)
    if not numero_telefono.isdigit() or len(
            numero_telefono) != 9 or numero_telefono.startswith('0'):
        await event.reply(
            "El número de teléfono debe tener 9 dígitos y no puede comenzar con un 0.",
            parse_mode='markdown')
        return

    # Aplicar antispam
    is_spam = await handle_antispam(event, username)
    if is_spam:
        return  # Detener si el antispam está activo

    # Enviar mensaje inicial de búsqueda
    searching_message = await event.reply("🔍 𝐁𝐮𝐬𝐜𝐚𝐧𝐝𝐨 𝐨𝐩𝐞𝐫𝐚𝐝𝐨𝐫....",
                                          parse_mode='markdown')

    try:
        # Ejecutar la función de verificación del operador de forma asíncrona
        loop = asyncio.get_running_loop()
        operador = await loop.run_in_executor(None, vernum.verificar_operador,
                                              numero_telefono)

        # Verificar si se obtuvo un resultado válido
        if operador and operador.lower() not in [
                "resultado no encontrado , ¿numero chueco?",
                "𝐫𝐞𝐬𝐮𝐥𝐭𝐚𝐝𝐨 𝐧𝐨 𝐞𝐧𝐜𝐨𝐧𝐭𝐫𝐚𝐝𝐨 , ¿𝐧𝐮𝐦𝐞𝐫𝐨 𝐜𝐡𝐮𝐞𝐜𝐨?"
        ]:
            # Mensaje según el operador detectado
            if "claro" in operador.lower():
                recomendacion = "/clax"
            elif "bitel" in operador.lower():
                recomendacion = "/bitx"
            elif "movistar" in operador.lower():
                recomendacion = "/telp"
            elif "entel" in operador.lower():
                recomendacion = "/telp"

            # Editar el mensaje de búsqueda con el resultado final
            await searching_message.edit(
                f"⚡ 𝗢𝗣𝗘𝗥𝗔𝗗𝗢𝗥 𝗘𝗡𝗖𝗢𝗡𝗧𝗥𝗔𝗗𝗢 𝗗𝗘𝗟 𝗡𝗨𝗠𝗘𝗥𝗢 {numero_telefono}\n→ {operador}\n\n"
                f"☎️ 𝗕𝗨𝗦𝗤𝗨𝗘𝗗𝗔 𝗘𝗫𝗜𝗧𝗢𝗦𝗔\n\n💡 𝗨𝗦𝗔 `{recomendacion} {numero_telefono}` 𝗣𝗔𝗥𝗔 𝗖𝗢𝗡𝗢𝗖𝗘𝗥 𝗟𝗢𝗦 𝗗𝗔𝗧𝗢𝗦",
                parse_mode='markdown')

            # Reducir los créditos si no tiene un plan activo
            reducir_creditos(user_data, precio_comando, username)

        else:
            await searching_message.edit(
                "𝐑𝐞𝐬𝐮𝐥𝐭𝐚𝐝𝐨 𝐧𝐨 𝐞𝐧𝐜𝐨𝐧𝐭𝐫𝐚𝐝𝐨 , ¿𝐍𝐮𝐦𝐞𝐫𝐨 𝐜𝐡𝐮𝐞𝐜𝐨?",
                parse_mode='markdown')

    except Exception as e:
        # Manejo de errores inesperados durante la verificación
        await searching_message.edit(
            "⚠️ Hubo un error durante la búsqueda. Inténtalo de nuevo más tarde."
        )
        print(f"Error en vernum_command: {e}")


broadcast_messages = {}  # Diccionario para registrar los mensajes enviados


@client.on(events.NewMessage(pattern='/msj'))
async def broadcast_message(event):
    sender = await event.get_sender()
    username = sender.username

    if username not in owners:
        await client.send_message(
            event.chat_id, "❌ No tienes permiso para usar este comando.")
        return

    await client.send_message(
        event.chat_id,
        "Escribe el mensaje que deseas enviar (usa `{username}` para personalizar con el nombre del usuario). "
        "Adjunta una imagen opcional y envíala como respuesta.")

    @client.on(
        events.NewMessage(
            func=lambda e: e.is_reply and e.sender_id == sender.id))
    async def capture_message(reply_event):
        message_text = reply_event.message.message
        image = reply_event.message.media

        buttons = [[
            Button.inline("Añadir Botones", b"add_buttons"),
            Button.inline("Enviar Sin Botones", b"send_without_buttons")
        ], [Button.inline("❌ Cancelar", b"cancel_broadcast")]]

        await client.send_message(
            reply_event.chat_id,
            "¿Deseas añadir botones al mensaje o enviarlo directamente?",
            buttons=buttons)

        selected_buttons = []
        button_states = {
            "button_akdios": False,
            "button_group": False,
            "button_serlegacy": False,
            "button_yuta": False,
            "button_okarun": False
        }

        @client.on(events.CallbackQuery)
        async def handle_button_selection(callback_event):
            nonlocal selected_buttons, button_states

            if callback_event.data == b"cancel_broadcast":
                await callback_event.edit("❌ Proceso cancelado.")
                return

            if callback_event.data == b"send_without_buttons":
                await send_broadcast_to_users(message_text, image, [])
                await callback_event.edit(
                    "✅ Mensaje enviado a todos los usuarios registrados.")
                return

            if callback_event.data == b"add_buttons":
                await update_buttons_ui(callback_event, button_states)
                return

            if callback_event.data == b"confirm_send":
                await preview_message(callback_event, message_text, image,
                                      selected_buttons)
                return

            # Actualizar estados de botones seleccionados
            key = callback_event.data.decode("utf-8")
            if key in button_states:
                button_states[key] = not button_states[key]

                if button_states[key]:  # Si se selecciona
                    if key == "button_akdios":
                        selected_buttons.append(
                            Button.url("🍂 Akdios", "https://t.me/Akdios"))
                    elif key == "button_group":
                        selected_buttons.append(
                            Button.url("🌐 Grupo Principal",
                                       "https://t.me/pisllingdox"))

                        selected_buttons.append(
                            Button.url("🔥 Yuta Faster",
                                       "https://t.me/yuta_faster"))
                    elif key == "button_okarun":
                        selected_buttons.append(
                            Button.url("⚡ OKARUN_7", "https://t.me/OKARUN_7"))
                else:  # Si se deselecciona
                    selected_buttons = [
                        b for b in selected_buttons
                        if b.url != f"https://t.me/{key.split('_')[1]}"
                    ]

                await update_buttons_ui(callback_event, button_states)


async def update_buttons_ui(callback_event, button_states):
    buttons = [
        [
            Button.inline(
                f"Botón a @AKdios{' (Seleccionado)' if button_states['button_akdios'] else ''}",
                b"button_akdios"),
            Button.inline(
                f"Botón al Grupo{' (Seleccionado)' if button_states['button_group'] else ''}",
                b"button_group")
        ],
        [
            Button.inline(
                f"Botón a @yuta_faster{' (Seleccionado)' if button_states['button_yuta'] else ''}",
                b"button_yuta")
        ],
        [
            Button.inline(
                f"Botón a @OKARUN_7{' (Seleccionado)' if button_states['button_okarun'] else ''}",
                b"button_okarun")
        ],
        [
            Button.inline("Confirmar y Enviar", b"confirm_send"),
            Button.inline("❌ Cancelar", b"cancel_broadcast")
        ]
    ]

    try:
        await callback_event.edit("Selecciona los botones que deseas añadir:",
                                  buttons=buttons)
    except RPCError as e:
        if "Content of the message was not modified" in str(e):
            print(
                "⚠️ Los botones no fueron modificados porque no hubo cambios.")
        else:
            print(f"❌ Error al actualizar los botones: {e}")


async def preview_message(callback_event, message_text, image, buttons):
    try:
        if buttons:
            await callback_event.respond(
                f"Vista previa del mensaje:\n\n{message_text}",
                file=image if image else None,
                buttons=buttons)
        await callback_event.respond("¿Deseas confirmar el envío del mensaje?",
                                     buttons=[[
                                         Button.inline("✅ Confirmar Envío",
                                                       b"final_send"),
                                         Button.inline("❌ Cancelar",
                                                       b"cancel_broadcast")
                                     ]])

        @client.on(events.CallbackQuery)
        async def confirm_send(final_event):
            if final_event.data == b"final_send":
                await send_broadcast_to_users(message_text, image, buttons)
                await final_event.edit(
                    "✅ Mensaje enviado a todos los usuarios registrados.")
            elif final_event.data == b"cancel_broadcast":
                await final_event.edit("❌ Proceso cancelado.")
    except RPCError as e:
        print(f"❌ Error en la vista previa: {e}")


async def send_broadcast_to_users(message, image, buttons):
    users_data = load_user_data()  # Cargar usuarios registrados
    registered_users = list(users_data.keys())
    successful = 0  # Contador de envíos exitosos
    failed = []  # Lista de usuarios fallidos

    for user in registered_users:
        try:
            # Validar si el usuario es válido
            entity = await client.get_input_entity(user)
            personalized_message = message.replace("{username}", f"@{user}")

            valid_buttons = buttons if buttons else None

            if image:
                await client.send_file(entity,
                                       image,
                                       caption=personalized_message,
                                       buttons=valid_buttons)
            else:
                await client.send_message(entity,
                                          personalized_message,
                                          buttons=valid_buttons)

            # Registrar mensaje enviado
            if user not in broadcast_messages:
                broadcast_messages[user] = []
            broadcast_messages[user].append(
                f"Mensaje enviado exitosamente a {user}")

            print(f"✅ Mensaje enviado a {user}.")
            successful += 1
        except (UsernameNotOccupiedError, ValueError, PeerIdInvalidError):
            print(
                f"⚠️ No se pudo enviar el mensaje a {user}: Usuario no válido."
            )
            failed.append(user)
        except RPCError as e:
            print(f"❌ Error al enviar mensaje a {user}: {e}")
            failed.append(user)

    # Resultados
    print(f"✅ Envíos exitosos: {successful}")
    print(f"⚠️ Fallos: {len(failed)}")
    if failed:
        print(f"⚠️ Usuarios no válidos: {', '.join(failed)}")


@client.on(events.NewMessage(pattern='/delmsj'))
async def delete_broadcasts(event):
    sender = await event.get_sender()
    username = sender.username

    if username not in owners:
        await client.send_message(
            event.chat_id, "❌ No tienes permiso para usar este comando.")
        return

    if not broadcast_messages:
        await client.send_message(event.chat_id,
                                  "❌ No hay mensajes previos para eliminar.")
        return

    for user, message_ids in broadcast_messages.items():
        for message_id in message_ids[-1:]:
            try:
                await client.delete_messages(user, message_id)
                print(f"✅ Mensaje eliminado de {user}.")
            except RPCError as e:
                print(f"❌ Error al eliminar mensaje de {user}: {e}")

    broadcast_messages.clear()
    await client.send_message(
        event.chat_id, "✅ Últimos mensajes eliminados de todos los chats.")


original_messages = {}


@client.on(events.NewMessage(pattern='/buy'))
async def buy(event):
    buy_text = """
    🇵🇪 𝗣𝗥𝗘𝗖𝗜𝗢𝗦 #ℙ𝕀𝕊𝕃𝕃𝕀ℕ𝔾_𝔻𝕆𝕏
「 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 𝗬 𝗣𝗟𝗔𝗡𝗘𝗦 」🇵🇪

➥ 𝗣𝗥𝗘𝗖𝗜𝗢 𝗗𝗘 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦

🔖 𝟯𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟳 𝗦𝗢𝗟𝗘𝗦
🔖 𝟭𝟭𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟭𝟮 𝗦𝗢𝗟𝗘𝗦
🔖 𝟮𝟴𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟮𝟮 𝗦𝗢𝗟𝗘𝗦
🔖 𝟰𝟱𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟯𝟱 𝗦𝗢𝗟𝗘𝗦
🔖 𝟱𝟵𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟰𝟱 𝗦𝗢𝗟𝗘𝗦
🔖 𝟭𝟱𝟬𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟵𝟬 𝗦𝗢𝗟𝗘𝗦

➥ 𝗣𝗥𝗘𝗖𝗜𝗢 𝗗𝗘 𝗣𝗟𝗔𝗡𝗘𝗦 𝗜𝗟𝗜𝗠𝗜𝗧𝗔𝗗𝗢

🎯 𝟳 𝗗𝗜𝗔𝗦 ➥ 𝟭𝟬 𝗦𝗢𝗟𝗘𝗦
🎯 𝟭𝟱 𝗗𝗜𝗔𝗦 ➥ 𝟮𝟬 𝗦𝗢𝗟𝗘𝗦
🎯 𝟯𝟬 𝗗𝗜𝗔𝗦 ➥ 𝟰𝟬 𝗦𝗢𝗟𝗘𝗦
🎯 𝟲𝟬 𝗗𝗜𝗔𝗦 ➥ 𝟳𝟱 𝗦𝗢𝗟𝗘𝗦

📣 𝗡𝗨𝗘𝗦𝗧𝗥𝗢 𝗕𝗢𝗧 𝗡𝗢 𝗧𝗜𝗘𝗡𝗘 𝗥𝗔𝗡𝗚𝗢𝗦,  𝗣𝗢𝗗𝗥𝗔𝗦 𝗔𝗖𝗖𝗘𝗗𝗘𝗥 𝗔 𝗟𝗢𝗦 𝗖𝗢𝗠𝗔𝗡𝗗𝗢𝗦 𝗦𝗜𝗡 𝗥𝗘𝗦𝗧𝗥𝗜𝗖𝗖𝗜𝗢𝗡, 𝗬𝗔 𝗦𝗘𝗔 𝗤𝗨𝗘 𝗖𝗢𝗠𝗣𝗥𝗘𝗦 𝗗𝗜𝗔𝗦 𝗢 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦.

➥ 𝗩𝗘𝗡𝗗𝗘𝗗𝗢𝗥𝗘𝗦 𝗢𝗙𝗜𝗖𝗜𝗔𝗟𝗘𝗦 ⬎
    """

    buttons = [[Button.url("☀️ 𝗔𝗞𝗗𝗜𝗢𝗦 ", "https://t.me/AKdios")],
               [Button.url("🌩 𝗢𝗞𝗔𝗥𝗨𝗡", "https://t.me/OKARUN_7")]]

    # Ruta a la imagen
    image_path = "buy.png"

    # Enviar la imagen primero
    await client.send_file(event.chat_id,
                           file=image_path,
                           caption=buy_text,
                           buttons=buttons)


admin_commands_list = """
🔧 **Comandos de Administración** 🔧

- `/activate`: Activa el bot en el grupo actual.
- `/desactivate`: Desactiva el bot en el grupo actual.
- `/addprem <cantidad> d|m @usuario`: Añade días o monedas de premium al usuario.
- `/unprem <cantidad> d|m @usuario`: Elimina días o monedas de premium al usuario.
- `/addowner @usuario`: Añade un usuario como propietario.
- `/addseller @usuario`: Añade un usuario como vendedor.
- `/bangrupo`: Banea al bot en todos los grupos.
- `/banpriv`: Banea al bot en todos los chats privados.
- `/banglobal`: Banea al bot en todos los lados.
- `/unbangrupo`: Desbanea al bot en todos los grupos.
- `/unbanpriv`: Desbanea al bot en todos los chats privados.
- `/unbanglobal`: Desbanea al bot en todos los lados.
- `/rol @usuario`: Cambia el rol de un usuario.
- `/info @usuario`: Muestra la información de otro usuario.
- `/listusuarios`: Lista todos los usuarios registrados.
- `/consultas`: Muestra el número de consultas realizadas.
- `/resetwarn @usuario`: Resetea las advertencias de un usuario.
- `/resetcoins @usuario`: Resetea las monedas de un usuario.
- `/resetprem @usuario`: Resetea el estado premium de un usuario.
- `/blockdata <data>`: Bloquea un dato específico.
- `/unblockdata <data>`: Desbloquea un dato específico.
- `/sendmsg @usuario <mensaje>`: Envía un mensaje a un usuario específico.
- `/globalmsg <mensaje>`: Envía un mensaje a todos los usuarios.
- `/backupdata`: Hace un respaldo de los datos de los usuarios.
- `/restoredata`: Restaura los datos de los usuarios desde el respaldo.
- `/setprice <comando> <precio>`: Establece el precio de un comando.
- `/banuser @usuario`: Banea a un usuario específico.
- `/unbanuser @usuario`: Desbanea a un usuario específico.
- `/addcoin @usuario <cantidad>`: Añade monedas a un usuario.
- `/removecoin @usuario <cantidad>`: Elimina monedas de un usuario.
- `/addquery @usuario <cantidad>`: Añade consultas a un usuario.
- `/removequery @usuario <cantidad>`: Elimina consultas de un usuario.
"""

help_text = """
ℹ️ **Ayuda del Bot** ℹ️

- `/cmds`: Lista de comandos disponibles
- `/addprem <cantidad> d|m @usuario`: Añade días o monedas de premium al usuario
- `/unprem <cantidad> d|m @usuario`: Elimina días o monedas de premium al usuario
- `/addowner @usuario`: Añade un usuario como propietario
- `/addseller @usuario`: Añade un usuario como vendedor
- `/help`: Muestra esta ayuda
- `/status`: Muestra el estado del bot
- `/register`: Regístrate en el bot para usar los comandos
- `/buy`: Muestra la información de precios para comprar monedas o premium
- `/blocklist`: Muestra la lista de datos bloqueados
- `/bangrupo`: Banea al bot en todos los grupos
- `/banpriv`: Banea al bot en todos los chats privados
- `/banglobal`: Banea al bot en todos los lados
- `/unbangrupo`: Desbanea al bot en todos los grupos
- `/unbanpriv`: Desbanea al bot en todos los chats privados
- `/unbanglobal`: Desbanea al bot en todos los lados
- `/me`: Muestra tu información de usuario
- `/info @usuario`: Muestra la información de otro usuario
"""

# Diccionario para registrar el último mensaje procesado por cada usuario
last_message_id = {}
last_command_valid_time = {}

# Diccionario de cooldowns personalizados
cooldowns = {
    "default": 35,  # Cooldown estándar en segundos
    "leo_vidal_username": 0,  # Sin antispam
    "Josepapu14": 0  # Sin antispam
}


async def handle_antispam(event, username):
    # Verificar si el usuario está exento del antispam
    if username in cooldowns and cooldowns[username] == 0:
        return False  # No activar antispam para este usuario

    # Verificar si el mensaje es un comando (empieza con '/')
    if not event.message.message.startswith('/'):
        return False  # No es un comando, no aplicar antispam

    # Obtener el tiempo actual
    current_time = datetime.now()

    # Verificar si el mensaje actual ya fue procesado
    if last_message_id.get(username) == event.message.id:
        print(
            f"Antispam: Mensaje duplicado detectado para {username}. Ignorando."
        )
        return True  # Mensaje ya procesado

    # Guardar el ID del mensaje actual
    last_message_id[username] = event.message.id

    # Obtener el tiempo del último comando válido
    last_command_time = last_command_valid_time.get(username, datetime.min)

    # Obtener el tiempo de cooldown para el usuario
    cooldown = cooldowns.get(username, cooldowns["default"])
    time_since_last_command = (current_time -
                               last_command_time).total_seconds()

    # Si no ha pasado el cooldown, activar antispam
    if time_since_last_command < cooldown:
        time_left = cooldown - time_since_last_command
        await event.reply(
            f"[🚫] 𝗝𝗢𝗗𝗘𝗥, 𝗠𝗔𝗦 𝗗𝗘𝗦𝗣𝗔𝗖𝗜𝗢 𝗩𝗘𝗟𝗢𝗖𝗜𝗦𝗧𝗔, 𝗘𝗦𝗣𝗘𝗥𝗔 {int(time_left)} 𝗦𝗘𝗚𝗨𝗡𝗗𝗢𝗦.",
            parse_mode='markdown')
        print(
            f"Antispam: Usuario {username} debe esperar {int(time_left)} segundos."
        )
        return True  # Indicar que el antispam está activo

    # Actualizar el tiempo del último comando válido
    last_command_valid_time[username] = current_time
    return False  # Antispam no está activo


status_text = """
📊 **Estado del Bot** 📊

- Usuarios premium: {premium_count} 🌟
- Comandos ejecutados por usuarios no premium: {non_premium_count} 🔍
"""

blocklist_text = """
🚫 **Datos Bloqueados** 🚫

- **Nombres:** {names}
- **Números:** {numbers}
- **DNI:** {dni}
"""


def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def load_user_data():
    try:
        with open(user_data_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_user_data(data):
    with open(user_data_file, 'w') as f:
        json.dump(data, f, indent=4)


def get_user_data(username):
    data = load_user_data()
    user_data = data.get(
        username, {
            "premium_start": None,
            "premium_end": None,
            "registered": False,
            "coins": 0,
            "warnings": 0,
            "role": "NO CLIENTE",
            "anti_spam": 0,
            "queries": 0,
            "joined": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    if "premium_start" not in user_data:
        user_data["premium_start"] = None
    if "premium_end" not in user_data:
        user_data["premium_end"] = None
    if "registered" not in user_data:
        user_data["registered"] = False
    if "coins" not in user_data:
        user_data["coins"] = 0
    if "warnings" not in user_data:
        user_data["warnings"] = 0
    if "role" not in user_data:
        user_data["role"] = "NO CLIENTE"
    if "anti_spam" not in user_data:
        user_data["anti_spam"] = 0
    if "queries" not in user_data:
        user_data["queries"] = 0
    if "joined" not in user_data:
        user_data["joined"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return user_data


def cargar_id_data():
    if os.path.exists(ID_FILE):
        with open(ID_FILE, 'r') as f:
            return json.load(f)
    return {}


def guardar_id_data(id_data):
    with open(ID_FILE, 'w') as f:
        json.dump(id_data, f, indent=4)


def verificar_usuario_registrado(user_id):
    id_data = cargar_id_data()
    return str(user_id) in id_data


def registrar_usuario_id(user_id, first_name, last_name):
    id_data = cargar_id_data()
    id_data[str(user_id)] = {"first_name": first_name, "last_name": last_name}
    guardar_id_data(id_data)


def update_user_data(username, data):
    all_data = load_user_data()
    all_data[username] = data
    save_user_data(all_data)


def save_seller_data(data):
    with open('seller_data.json', 'w') as f:
        json.dump(data, f, indent=4)


def load_seller_data():
    try:
        with open('seller_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


seller_data = load_seller_data()


def load_active_groups():
    return load_json(active_groups_file)


def save_active_groups(data):
    save_json(data, active_groups_file)


def is_data_blocked(data):
    data = data.lower()
    return data in blocked_data["names"] or data in blocked_data[
        "numbers"] or data in blocked_data["dni"]


async def handle_special_commands(event, command):
    sender = await event.get_sender()
    username = sender.username

    print(f"handle_special_commands: Comando={command}, Usuario={username}")

    if command == '/start':
        user_data = get_user_data(username)
        if not user_data["registered"]:
            await event.reply(
                "🇵🇪¡𝗕𝗜𝗘𝗡𝗩𝗘𝗡𝗜𝗗𝗢 𝗔 #ℙ𝕀𝕊𝕃𝕃𝕀ℕ𝔾_𝔻𝕆𝕏!. \n\n● 𝗣𝗥𝗜𝗠𝗘𝗥𝗢 𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗔𝗧𝗘  /register\n● 𝗖𝗢𝗠𝗣𝗥𝗔 𝗨𝗡 𝗣𝗟𝗔𝗡  /buy\n● 𝗥𝗘𝗩𝗜𝗦𝗔 𝗧𝗨 𝗣𝗟𝗔𝗡  /me\n● 𝗨𝗦𝗔 𝗟𝗢𝗦 𝗖𝗢𝗠𝗔𝗡𝗗𝗢𝗦  /cmds\n\n⚜️ 𝗢𝗪𝗡𝗘𝗥𝗦:\n@AKDIOS ● @OKARUN_7\n\n🧬 𝗚𝗥𝗨𝗣𝗢 𝗢𝗙𝗜𝗖𝗜𝗔𝗟:\nhttps://t.me/+MPa0oFwz_fgwM2Fh",
                parse_mode='markdown')
        else:
            await event.reply(
                "🇵🇪¡𝗕𝗜𝗘𝗡𝗩𝗘𝗡𝗜𝗗𝗢 𝗔 #ℙ𝕀𝕊𝕃𝕃𝕀ℕ𝔾_𝔻𝕆𝕏!. \n\n● 𝗣𝗥𝗜𝗠𝗘𝗥𝗢 𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗔𝗧𝗘  /register\n● 𝗖𝗢𝗠𝗣𝗥𝗔 𝗨𝗡 𝗣𝗟𝗔𝗡  /buy\n● 𝗥𝗘𝗩𝗜𝗦𝗔 𝗧𝗨 𝗣𝗟𝗔𝗡  /me\n● 𝗨𝗦𝗔 𝗟𝗢𝗦 𝗖𝗢𝗠𝗔𝗡𝗗𝗢𝗦  /cmds\n\n⚜️ 𝗢𝗪𝗡𝗘𝗥𝗦:\n@AKDIOS ● @OKARUN_7\n\n🧬 𝗚𝗥𝗨𝗣𝗢 𝗢𝗙𝗜𝗖𝗜𝗔𝗟:\nhttps://t.me/+MPa0oFwz_fgwM2Fh",
                parse_mode='markdown')

    elif command == '/ad' and username in owners:
        await event.reply(admin_commands_list, parse_mode='markdown')
    elif command == '/help':
        await event.reply(help_text, parse_mode='markdown')
    elif command == '/status':
        all_data = load_user_data()
        premium_count = sum(
            1 for user in all_data.values() if user['premium_end']
            and parse_date(user['premium_end']) > datetime.now())
        non_premium_count = sum(user_command_count.values())
        await event.reply(status_text.format(
            premium_count=premium_count, non_premium_count=non_premium_count),
                          parse_mode='markdown')

    elif command == '/register':
        user_data = get_user_data(username)
        if not user_data["registered"]:
            if username:
                user_data["registered"] = True
                user_data["joined"] = datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S')
                if username in owners:
                    user_data["premium_end"] = "30/12/31"
                    user_data["role"] = "OWNER"
                else:
                    user_data["premium_end"] = None
                    user_data["role"] = "CLIENTE"
                update_user_data(username, user_data)
                welcome_message = f"""
🎉 **¡Bienvenido/a {username}!** 🎉
📋 Registro completado exitosamente.

🛠 **Información de tu perfil**:

- **ID:** {sender.id}
- **Nombre:** {username}
- **Usuario:** @{username}
- **Rol:** {user_data.get('role', 'NO CLIENTE')}
- **Créditos:** {user_data.get('coins', 0)}
- **Estado:** ACTIVO
- **Anti-Spam:** {user_data.get('anti_spam', 0)}
- **Consultas:** {user_data.get('queries', 0)}
- **Unido:** {user_data.get('joined')}
"""
                await event.reply(welcome_message, parse_mode='markdown')
                print(f"Usuario registrado: {username}")
            else:
                await event.reply(
                    "[⚠️] 𝗣𝗢𝗥 𝗙𝗔𝗩𝗢𝗥 𝗖𝗢𝗡𝗙𝗜𝗚𝗨𝗥𝗔 𝗧𝗨 𝗡𝗢𝗠𝗕𝗥𝗘 𝗗𝗘 𝗨𝗦𝗨𝗔𝗥𝗜𝗢 𝗘𝗡 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 𝗣𝗔𝗥𝗔 𝗧𝗨 𝗗𝗘𝗕𝗜𝗗𝗢 𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗢, 𝗦𝗜 𝗡𝗢 𝗦𝗔𝗕𝗘𝗦 𝗖𝗢𝗠𝗢 𝗛𝗔𝗖𝗘𝗥𝗟𝗢 𝗨𝗦𝗔 /tutorial"
                )
                print("Intento de registro sin nombre de usuario")
        else:
            await event.reply(
                "[✨] 𝗬𝗔 𝗧𝗘 𝗘𝗡𝗖𝗨𝗘𝗡𝗧𝗥𝗔𝗦 𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗔𝗗𝗢 𝗣𝗔𝗥𝗔 𝗨𝗦𝗔𝗥 𝗘𝗟 𝗕𝗢𝗧. ¿𝗖𝗢𝗡 𝗚𝗔𝗡𝗔𝗦 𝗗𝗘 𝗗𝗢𝗕𝗟𝗘 𝗗𝗜𝗩𝗘𝗥𝗦𝗜𝗢𝗡, 𝗘𝗡𝗧𝗢𝗡𝗖𝗘𝗦?",
                parse_mode='markdown')
            print(f"Intento de registro duplicado: {username}")
    elif command == '/blocklist':
        await event.reply(blocklist_text.format(
            names=", ".join(blocked_data["names"]),
            numbers=", ".join(blocked_data["numbers"]),
            dni=", ".join(blocked_data["dni"])),
                          parse_mode='markdown')
    elif command.startswith('/addprem') or command.startswith('/unprem'):
        parts = event.message.message.split()
        if event.is_reply:
            replied_msg = await event.get_reply_message()
            target_user = replied_msg.sender.username
        else:
            target_user = parts[3].lstrip('@') if len(parts) == 4 else None

        if target_user:
            cantidad = int(parts[1])
            unidad = parts[2].lower()
            user_data = get_user_data(target_user)

            if username in owners:
                # Lógica para owners
                if unidad == 'd':
                    current_premium_end = parse_date(
                        user_data["premium_end"]
                    ) if user_data["premium_end"] else datetime.now()
                    if command.startswith('/addprem'):
                        premium_end = current_premium_end + timedelta(
                            days=cantidad)
                        action = "añadidos"
                    elif command.startswith('/unprem'):
                        premium_end = current_premium_end - timedelta(
                            days=cantidad)
                        action = "removidos"
                    user_data["premium_end"] = premium_end.strftime('%d/%m/%y')

                    # Enviar notificación sobre cambio de días premium
                    await client.send_message(
                        notification_chat_id,
                        f"🔔 @{target_user} ha tenido {cantidad} días {action} de premium por @{username}."
                    )

                elif unidad == 'm':
                    if command.startswith('/addprem'):
                        user_data["coins"] += cantidad
                        action = "añadidas"
                    elif command.startswith('/unprem'):
                        user_data["coins"] -= cantidad
                        action = "removidas"

                # Enviar notificación sobre cambio de monedas
                    await client.send_message(
                        notification_chat_id,
                        f"🔔 @{target_user} ha tenido {cantidad} monedas {action} por @{username}."
                    )

            # Actualizar rol del usuario basado en sus nuevos estados de premium y monedas
                if user_data["coins"] > 0 or user_data["premium_end"]:
                    user_data["role"] = "CLIENTE"
                else:
                    user_data["role"] = "NO CLIENTE"

                update_user_data(target_user, user_data)
                await event.reply(
                    f"Se ha actualizado el saldo de {unidad} con éxito a @{target_user}.",
                    parse_mode='markdown')

            elif username in sellers:
                # Lógica para sellers
                seller_data_entry = get_seller_data(username)

                if unidad == 'm':  # Vender créditos
                    if seller_data_entry['assigned_credits'] < cantidad:
                        await event.reply(
                            f"No tienes suficientes créditos asignados para vender. Créditos disponibles: {seller_data_entry['assigned_credits']}.",
                            parse_mode='markdown')
                        return
                    seller_data_entry['assigned_credits'] -= cantidad

                    # Registrar la venta de créditos
                    seller_data_entry['sold_credits'].append({
                        "cantidad":
                        cantidad,
                        "comprador":
                        target_user,
                        "fecha":
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "vendido_por":
                        username
                    })

                elif unidad == 'd':  # Vender días
                    if seller_data_entry['assigned_days'] < cantidad:
                        await event.reply(
                            f"No tienes suficientes días asignados para vender. Días disponibles: {seller_data_entry['assigned_days']}.",
                            parse_mode='markdown')
                        return
                    seller_data_entry['assigned_days'] -= cantidad

                    # Registrar la venta de días
                    seller_data_entry['sold_days'].append({
                        "cantidad":
                        cantidad,
                        "comprador":
                        target_user,
                        "fecha":
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "vendido_por":
                        username
                    })

            # Actualizar datos del seller en seller_data.json
                update_seller_data(username, seller_data_entry)

                # Actualizar datos del usuario objetivo en user_data.json
                if unidad == 'm':
                    user_data['coins'] += cantidad
                elif unidad == 'd':
                    premium_end_date = parse_date(
                        user_data['premium_end']
                    ) if user_data['premium_end'] else datetime.now()
                    new_premium_end = premium_end_date + timedelta(
                        days=cantidad)
                    user_data['premium_end'] = new_premium_end.strftime(
                        '%d/%m/%y')

                update_user_data(target_user, user_data)

                # Confirmación de la operación
                await event.reply(
                    f"Se han añadido {cantidad} {unidad} a @{target_user} exitosamente.",
                    parse_mode='markdown')

        else:
            await event.reply(
                "Formato incorrecto. Uso correcto: /addprem <cantidad> d|m @usuario o /unprem <cantidad> d|m @usuario, o respondiendo a su mensaje.",
                parse_mode='markdown')

    elif command.startswith('/addseller'):
        if username in owners:
            parts = event.message.message.split()
            if event.is_reply:
                replied_msg = await event.get_reply_message()
                new_seller = replied_msg.sender.username
            else:
                new_seller = parts[1].lstrip('@') if len(parts) == 2 else None

            if new_seller:
                # Cargar los datos actuales de sellers en tiempo real
                seller_data = load_seller_data()

                if new_seller not in sellers:
                    sellers.append(new_seller)

                    # Obtener o crear los datos del usuario
                    user_data = get_user_data(new_seller)
                    user_data["role"] = "SELLER"  # Cambiar el rol a "SELLER"

                    # Actualizar el archivo JSON con los nuevos datos del seller
                    update_user_data(new_seller, user_data)

                    # Inicializar datos específicos del seller en seller_data.json si no existe
                    if new_seller not in seller_data:
                        seller_data[new_seller] = {
                            "assigned_credits": 0,
                            "assigned_days": 0,
                            "sold_credits": [],
                            "sold_days": [],
                            "clients": {
                            }  # Nuevo campo para almacenar clientes del vendedor
                        }
                        save_seller_data(seller_data)

                    await event.reply(
                        f"@{new_seller} ha sido añadido como vendedor con permisos de venta.",
                        parse_mode='markdown')
                else:
                    await event.reply(f"@{new_seller} ya es vendedor.",
                                      parse_mode='markdown')
            else:
                await event.reply(
                    "Formato incorrecto. Uso correcto: /addseller @usuario o respondiendo a su mensaje.",
                    parse_mode='markdown')
        else:
            await event.reply("No tienes permiso para usar este comando.",
                              parse_mode='markdown')

    elif command == '/bangrupo':
        if username in owners:
            global_ban_status["group_ban"] = True
            await event.reply("❌ El bot ha sido baneado en todos los grupos.",
                              parse_mode='markdown')
        else:
            await event.reply("No tienes permiso para usar este comando.",
                              parse_mode='markdown')
    elif command == '/banpriv':
        if username in owners:
            global_ban_status["private_ban"] = True
            await event.reply(
                "❌ El bot ha sido baneado en todos los chats privados.",
                parse_mode='markdown')
        else:
            await event.reply("No tienes permiso para usar este comando.",
                              parse_mode='markdown')
    elif command == '/banglobal':
        if username in owners:
            global_ban_status["global_ban"] = True
            await event.reply("❌ El bot ha sido baneado globalmente.",
                              parse_mode='markdown')
        else:
            await event.reply("No tienes permiso para usar este comando.",
                              parse_mode='markdown')
    elif command == '/unbangrupo':
        if username in owners:
            global_ban_status["group_ban"] = False
            await event.reply(
                "✅ El bot ha sido desbaneado en todos los grupos.",
                parse_mode='markdown')
        else:
            await event.reply("No tienes permiso para usar este comando.",
                              parse_mode='markdown')
    elif command == '/unbanpriv':
        if username in owners:
            global_ban_status["private_ban"] = False
            await event.reply(
                "✅ El bot ha sido desbaneado en todos los chats privados.",
                parse_mode='markdown')
        else:
            await event.reply("No tienes permiso para usar este comando.",
                              parse_mode='markdown')
    elif command == '/unbanglobal':
        if username in owners:
            global_ban_status["global_ban"] = False
            await event.reply("✅ El bot ha sido desbaneado globalmente.",
                              parse_mode='markdown')
        else:
            await event.reply("No tienes permiso para usar este comando.",
                              parse_mode='markdown')
    elif command == '/me':
        user_data = get_user_data(username)

        # Verificar si el usuario está registrado
        if not user_data["registered"]:
            # Mensaje elegante invitando al registro con estilo de letra diferente
            await event.reply("""
     𝗕𝗶𝗲𝗻𝘃𝗲𝗻𝗶𝗱𝗼 𝗮𝗹 𝗦𝗶𝘀𝘁𝗲𝗺𝗮 𝗱𝗲 𝗖𝗼𝗻𝘀𝘂𝗹𝘁𝗮𝘀.

     𝗣𝗮𝗿𝗮 𝗮𝗰𝗰𝗲𝗱𝗲𝗿 𝗮 𝘁𝗼𝗱𝗮𝘀 𝗹𝗮𝘀 𝗳𝘂𝗻𝗰𝗶𝗼𝗻𝗮𝗹𝗶𝗱𝗮𝗱𝗲𝘀, 𝗲𝘀 𝗻𝗲𝗰𝗲𝘀𝗮𝗿𝗶𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝗿𝘀𝗲.

     𝗣𝗼𝗿 𝗳𝗮𝘃𝗼𝗿, 𝘂𝘁𝗶𝗹𝗶𝘇𝗮 𝗲𝗹 𝗰𝗼𝗺𝗮𝗻𝗱𝗼:

     `/register`

     𝗚𝗿𝗮𝗰𝗶𝗮𝘀 𝗽𝗼𝗿 𝘂𝗻𝗶𝗿𝘁𝗲 𝗮 𝗻𝗼𝘀𝗼𝘁𝗿𝗼𝘀.
             """,
                              parse_mode='markdown')
        else:
            # Usuario registrado: mostrar el perfil del usuario con estilo de letra diferente
            premium_end = user_data.get("premium_end")
            has_premium = premium_end and datetime.strptime(
                premium_end, '%d/%m/%y') > datetime.now()
            plan = f'𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗵𝗮𝘀𝘁𝗮 {premium_end}' if has_premium else '𝗙𝗥𝗘𝗘'

            user_profile = f"""
🌩 𝗣𝗘𝗥𝗙𝗜𝗟 𝗗𝗘 {username}:

[🗿] 𝗜𝗗:  {sender.id}
[👩‍💻] 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘: {username}
[👤] 𝗡𝗜𝗖𝗞𝗡𝗔𝗠𝗘: @{username if username else '𝗦𝗶𝗻 𝘂𝘀𝗲𝗿𝗻𝗮𝗺𝗲'}
[💎] 𝗠𝗘𝗠𝗕𝗥𝗘𝗦𝗜𝗔:  {user_data.get('role', '𝗡𝗢 𝗖𝗟𝗜𝗘𝗡𝗧𝗘')}
[⏳] 𝗖𝗔𝗗𝗨𝗖𝗜𝗗𝗔𝗗 𝗩𝗜𝗣: {plan}
[💰] 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦: {user_data.get('coins', 0)}
[❄️] 𝗔𝗡𝗧𝗜-𝗦𝗣𝗔𝗠: {user_data.get('anti_spam', 0)}
[🔢] 𝗡° 𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗦:  {user_data.get('queries', 0)}
[📅] 𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗢: {user_data.get('joined', datetime.now().strftime('%y-%m-%d %H:%M:%S'))}
        """
            await event.reply(user_profile, parse_mode='markdown')

    elif command.startswith('/info'):
        if username in owners or username in sellers:
            parts = event.message.message.split()
            if event.is_reply:
                replied_msg = await event.get_reply_message()
                target_user = replied_msg.sender.username
            else:
                target_user = parts[1].lstrip('@') if len(parts) == 2 else None
            if target_user:
                user_data = get_user_data(target_user)
                if user_data:
                    premium_end = user_data.get("premium_end")
                    has_premium = premium_end and datetime.strptime(
                        premium_end, '%d/%m/%y') > datetime.now()
                    plan = f'PREMIUM hasta {premium_end}' if has_premium else 'FREE'
                    user_profile = f"""

🌩 | 𝗜𝗡𝗙𝗢. 𝗗𝗘𝗟 𝗖𝗟𝗜𝗘𝗡𝗧𝗘: {target_user}:

[👤] 𝗜𝗗: {user_data.get('id', 'Desconocido')}
[🗿] 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘: {target_user}
[👩‍💻] 𝗡𝗜𝗖𝗞𝗡𝗔𝗠𝗘: @{target_user}
[💎] 𝗥𝗢𝗟: {user_data.get('role', 'NO CLIENTE')}
[📈] 𝗣𝗟𝗔𝗡: {plan}
[💰] 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦: {user_data.get('coins', 0)}
[👺] 𝗘𝗦𝗧𝗔𝗗𝗢: ACTIVO
[❄️] 𝗔𝗡𝗧𝗜-𝗦𝗣𝗔𝗠: {user_data.get('anti_spam', 0)}
[⏱] 𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗦: {user_data.get('queries', 0)}
[📅] 𝗦𝗘 𝗨𝗡𝗜𝗢: {user_data.get('joined', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
"""
                    await event.reply(user_profile, parse_mode='markdown')
                else:
                    await event.reply("🔍 Usuario no encontrado.",
                                      parse_mode='markdown')
            else:
                await event.reply(
                    "Formato incorrecto. Uso correcto: /info @usuario o respondiendo a su mensaje.",
                    parse_mode='markdown')
        else:
            await event.reply("No tienes permiso para usar este comando.",
                              parse_mode='markdown')
    elif command.startswith('/addid'):
        if username in owners:
            parts = event.message.message.split()
            if len(parts) == 2:
                group_id = parts[1]
                active_groups = load_active_groups()
                active_groups[group_id] = True
                save_active_groups(active_groups)
                await event.reply(
                    f"✅ El bot ha sido activado en el grupo {group_id}.",
                    parse_mode='markdown')
            else:
                await event.reply(
                    "Formato incorrecto. Uso correcto: /addid <id_grupo>",
                    parse_mode='markdown')
        else:
            await event.reply("No tienes permiso para usar este comando.",
                              parse_mode='markdown')


def parse_date(date_str):
    """
    Intenta analizar la fecha con diferentes formatos, incluyendo años de dos dígitos.
    """
    # Definir una lista de formatos posibles
    formatos_fecha = [
        '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%y', '%d-%m-%Y', '%d/%m/%y'
    ]

    for fmt in formatos_fecha:
        try:
            # Intentar parsear la fecha con cada formato
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # Si no se reconoce ningún formato, lanzar una excepción
    raise ValueError(f"Formato de fecha no reconocido: {date_str}")


def load_user_data():
    try:
        with open(user_data_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


user_data = load_user_data()


def get_user_info(username):
    return user_data.get(username, None)


# Definir las palabras clave que indican una respuesta fallida
failed_response_keywords = [
    "No se encontró información", "[ERROR]", "Formato incorrecto",
    "Consulta no exitosa", "[⚠] No se encontro información.",
    "[⚠] Formatos Incorrectos", "[⚠] Error Inesperado!",
    "No se encontro información"
]

original_messages = {}
pending_responses = defaultdict(list)
# Diccionario para registrar los comandos ya procesados
processed_commands = {}


# Función para obtener datos de un usuario desde un archivo JSON
def get_user_data(username, json_file_path='user_data.json'):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            user_data = json.load(file)
        return user_data.get(username, None)
    except FileNotFoundError:
        print(f"El archivo {json_file_path} no se encontró.")
        return None


# Función para analizar y convertir una fecha en el formato adecuado
def parse_date(date_str):
    try:
        return datetime.strptime(
            date_str, '%Y-%m-%d')  # Ajustar formato de fecha si es necesario
    except ValueError:
        print("Formato de fecha no válido")
        return None


def get_user_id_and_name(username, json_file_path='id.json'):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            user_data = json.load(file)
        # Buscar el usuario en el archivo por su username
        for user_id, user_info in user_data.items():
            if user_info.get("username") == username:
                return user_info
        return None
    except FileNotFoundError:
        print(f"El archivo {json_file_path} no se encontró.")
        return None


# Función para obtener otros datos del usuario desde user_data.json
def get_user_data(username, json_file_path='user_data.json'):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            user_data = json.load(file)
        return user_data.get(username, None)
    except FileNotFoundError:
        print(f"El archivo {json_file_path} no se encontró.")
        return None


# Función para analizar y convertir una fecha en el formato adecuado
def parse_date(date_str):
    try:
        # Ajustar el formato de la fecha según el formato que tienes en userdata.json
        return datetime.strptime(date_str, '%d/%m/%y')
    except ValueError:
        print(f"Formato de fecha no válido: {date_str}")
        return None


# Evento para mensajes entrantes
@client.on(events.NewMessage(incoming=True, from_users=leo_vidal_username))
async def forward_response(event):
    print(f"Respuesta recibida del bot de origen: {event.message.text}")

    # Obtener los datos del mensaje original si es una respuesta
    original_message_data = None
    if event.message.reply_to_msg_id:
        original_message_data = original_messages.get(
            event.message.reply_to_msg_id)

    # Verificar si hay datos originales
    if not original_message_data:
        return  # No hay datos originales, no podemos proceder

    # Asignar el chat de destino (grupo o chat individual)
    destination_chat_id = original_message_data.get('original_chat_id',
                                                    event.chat_id)

    # Obtener el ID del mensaje original
    original_id = original_message_data.get('original_id', event.message.id)

    # Extraer el username del usuario que ejecutó el comando
    original_username = original_message_data.get('original_username')

    # Obtener el ID y el nombre del usuario desde id.json
    user_info_id = get_user_id_and_name(original_username)

    if not user_info_id:
        print(
            f"No se encontró información en id.json para {original_username}")
        user_info_id = {
            "id": original_message_data.get('original_user_id'),
            "first_name": "Usuario",
            "last_name": ""
        }

    # Obtener otros datos como plan premium y monedas desde user_data.json
    user_info = get_user_data(original_username)

    if not user_info:
        user_info = {"premium_end": None, "coins": 0}

    # Actualizar los datos del usuario si es necesario
    update_user_data(original_username,
                     user_info)  # Aquí utilizamos original_username

    # Calcular días restantes del plan premium
    premium_end = user_info.get("premium_end")
    days_remaining = "N/A"

    if premium_end and premium_end.lower() != "null":
        premium_end_date = parse_date(premium_end)
        if premium_end_date:
            days_remaining = (premium_end_date - datetime.now()).days
        else:
            days_remaining = "Fecha no válida"

    # Evitar agregar información cuando el mensaje contiene "Cargando..."
    plan_info = ""
    if "Cargando..." not in event.message.message:
        plan_info = f"\n➥ 𝗣𝗟𝗔𝗡: {days_remaining} días restantes\n➥ 𝗖𝗢𝗜𝗡𝗦: {user_info.get('coins', 0)}"

    # Formatear el enlace de "Consultado por" usando los datos extraídos de id.json
    consultado_por = f"\n\n➥ 𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗢:  [{user_info_id.get('first_name')} {user_info_id.get('last_name')}](tg://user?id={user_info_id.get('id')})"

    # Texto original del mensaje
    message = event.message.message

    # Diccionario de reemplazos
    replacements = {
        'Cargando....':
        '[■■■■■■□□□□]',
        '•············[#FENIXBOT]·············•':
        '',
        '[#FENIXBOT]':
        '',
        '🪙 FenixCoins : ♾ → Jose':
        '',
        '🪙 FenixCoins : ♾ - Jose': '' ,
        'RAZON SOCIAL':
        '𝗗𝗘𝗡𝗢𝗠𝗜𝗡𝗔𝗖𝗜𝗢𝗡',
        'FECHA MOVIMIENTO':
        '𝗙𝗘𝗖𝗛𝗔 𝗠𝗢𝗩.',
        'NRO DOCUMENTO':
        '𝗡𝗥𝗢 𝗗𝗢𝗖𝗨𝗠𝗘𝗡𝗧𝗢',
        'PROCEDENCIA/DESTINO':
        '𝗗𝗘𝗦𝗧𝗜𝗡𝗢',
        'TIPO DOCUMENTO':
        '𝗧𝗜𝗣𝗢 𝗗𝗘 𝗗𝗢𝗖𝗨. ',
        'TIPO MOVIMIENTO':
        '𝗧𝗜𝗣𝗢 𝗠𝗢𝗩𝗜𝗠𝗜𝗘𝗡𝗧𝗢',
        'MODO : UNLIMITED LVL 3':
        '━━━━━━━━━━━━━━━━━━',
        'UBICACION':
        '𝗨𝗕𝗜𝗚𝗘𝗢',
        'DIRECCION':
        '𝗗𝗜𝗥𝗘𝗖𝗖𝗜𝗢𝗡',
        'RESULTADOS NOMBRES':
        '🔎 | 𝗛𝗜𝗦𝗧𝗢𝗥𝗜𝗔𝗟 𝗡𝗢𝗠𝗕𝗥𝗘𝗦',
        'SALDO':
        '𝗦𝗔𝗟𝗗𝗢',
        'PERIODO':
        '𝗣𝗘𝗥𝗜𝗢𝗗𝗢',
        'EMPRESA':
        '𝗘𝗡𝗧𝗜𝗗𝗔𝗗',
        'PLACA':
        '𝗣𝗟𝗔𝗖𝗔',
        'SERIE ':
        '𝗦𝗘𝗥𝗜𝗘',
        'NRO MOTOR':
        '𝗠𝗢𝗧𝗢𝗥',
        'MODELO':
        '𝗠𝗢𝗗𝗘𝗟𝗢',
        'MARCA':
        '𝗠𝗔𝗥𝗖𝗔',
        'SEDE':
        '𝗦𝗘𝗗𝗘',
        'COLOR':
        '𝗣𝗜𝗡𝗧𝗔𝗗𝗢',
        'ESTADO':
        '𝐄𝐒𝐓𝐀𝐃𝐎',
        'CIVIL':
        '𝗖𝗜𝗩𝗜𝗟',
        '[📍] PROPIETARIOS':
        '🚗 𝗣𝗥𝗢𝗣𝗜𝗘𝗧𝗔𝗥𝗜𝗢𝗦',
        'SITUACION':
        '𝗘𝗦𝗧𝗔𝗗𝗢',
        'CODIGO CUENTA':
        '𝗡𝗨𝗠𝗘𝗥𝗢 𝗗𝗘 𝗖𝗨𝗘𝗡𝗧𝗔',
        'CLASIFICACION':
        '𝗖𝗔𝗧𝗘𝗚𝗢𝗥𝗜𝗔\n ',
        'DEUDA':
        '𝗖𝗔𝗥𝗚𝗢',
        '🟢 NORMAL':
        '🟩 𝗛𝗔𝗕𝗜𝗧𝗨𝗔𝗟',
        '🟡 PROBLEMAS POTENCIALES':
        '🟨 𝗥𝗜𝗘𝗦𝗚𝗢𝗦𝗢',
        '🟠 DEFICIENTE':
        '🟧 𝗜𝗡𝗔𝗗𝗘𝗖𝗨𝗔𝗗𝗢 ',
        '🔴 DUDOSO':
        '🟥 𝗖𝗨𝗘𝗦𝗧𝗜𝗢𝗡𝗔𝗕𝗟𝗘',
        '⚫ PERDIDA':
        '🟫 𝗖𝗔𝗥𝗘𝗡𝗖𝗜𝗔',
        '[🚦] CLASIFICACION':
        '📊 𝗜𝗡𝗗𝗜𝗖𝗘:',
        'CODIGO':
        '𝗖.',
        '[ 💬 ] Buscando FICHA INFORMATIVA VEHÍCULAR en SUNARP de la ➜':
        '𝐁𝐮𝐬𝐜𝐚𝐧𝐝𝐨 𝐅𝐈𝐂𝐇𝐀 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐕𝐀 𝐕𝐄𝐇𝐈𝐂𝐔𝐋𝐀𝐑 𝐞𝐧 𝐒𝐔𝐍𝐀𝐑𝐏→',
        '[⚠] No se encontro informacion.':
        '[🚫] 𝗡𝗢 𝗛𝗔𝗬 𝗗𝗔𝗧𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦',
        '» Se encontraron':
        '→',
        'resultados en':
        '𝗿𝗲𝘀𝘂𝗹𝘁𝗮𝗱𝗼 𝗲𝗻𝗰𝗼𝗻𝘁𝗿𝗮𝗱𝗼 𝗲𝗻',
        '«':
        '🤖',
        '⚠️':
        '',
        'Credits : ♾️':
        '━━━━━━━━━━━━━━━━━━',
        'Wanted for : Jose':
        '',
        ':':
        '→',
        '[⚠] Este comando se encuentra en mantenimiento.':
        '[⚒️] 𝗘𝗡 𝗠𝗔𝗡𝗧𝗘𝗡𝗜𝗠𝗜𝗘𝗡𝗧𝗢',
        '[📃] ACTAS REGISTRADAS':
        '[🗂️] 𝗔𝗖𝗧𝗔𝗦 ',
        '•························•·························•':
        '━━━━━━━━━━━━━━━━━━',
        'RESULTADOS TELEFONOS TIEMPO REAL/ACTUALIZADOS':
        '☎️ | 𝗥𝗘𝗦𝗨𝗟𝗧𝗔𝗗𝗢 𝗧𝗘𝗟𝗘𝗙𝗢𝗡𝗜𝗔 ',
        '• RENIEC LVL 2':
        '🔍 | 𝗥𝗘𝗡𝗜𝗘𝗖 𝗢𝗡𝗟𝗜𝗡𝗘 | #ℙ𝕀𝕊𝕃𝕃𝕀ℕ𝔾_𝔻𝕆𝕏',
        '/Processing your request...':
        '❰🤖❱ 𝗖𝗢𝗡𝗦𝗨𝗟𝗧𝗔𝗡𝗗𝗢 ➟',
        'RESULTADOS SBS - REPORTE':
        '📊 𝗥𝗘𝗦𝗨𝗠𝗘𝗡 𝗗𝗘 𝗖𝗨𝗘𝗡𝗧𝗔𝗦',
        'RESULTADOS SBS - PADRON':
        '📊 𝗥𝗘𝗣𝗢𝗥𝗧𝗘 𝗦𝗕𝗦 𝗦𝗜𝗠𝗣𝗟𝗘',
        'RESULTADOS ARBOL GENEALOGICO':
        '🌳 | 𝗔𝗥𝗕𝗢𝗟 𝗚𝗘𝗡𝗘𝗔𝗟𝗢𝗚𝗜𝗖𝗢',
        'MENORES - AMARILLO':
        '𝙼𝙴𝙽𝙾𝚁𝙴𝚂 - 𝙰𝙼𝙰𝚁𝙸𝙻𝙻𝙾',
        'ULTIMOS REPORTES':
        '📊 𝗥𝗘𝗦𝗨𝗠𝗘𝗡 𝗗𝗘 𝗖𝗨𝗘𝗡𝗧𝗔𝗦',
        ' segundos para volver a utilizar este comando.':
        ' segundos antes de volver a intentarlo.',
        'MODO : UNLIMITED LVL 3​':
        'Ilimitado',
        'DNI PARTE ANVERSA GENERADA CORRECTAMENTE. ✅':
        '🪪 **SE HA GENERADO CON ÉXITO LA CARA FRONTAL DEL DNI.** ✅',
        'DNI PARTE REVERSA GENERADA CORRECTAMENTE. ✅':
        '🪪 **LA CARA POSTERIOR DEL DNI HA SIDO GENERADA EXITOSAMENTE.** ✅',
        'RESULTADOS TELEFONOS ACTUALIZADOS':
        '☎️ | 𝗧𝗘𝗟𝗘𝗙𝗢𝗡𝗢𝗦',
        'RESULTADOS TELEFONOS TIEMPO REAL':
        '☎️ | 𝗧𝗘𝗟𝗘𝗙𝗢𝗡𝗢𝗦',
        'DNI':
        '𝗗𝗡𝗜',
        'PLAN':
        '𝗣𝗟𝗔𝗡',
        'FUENTE':
        '𝗕𝗔𝗦𝗘',
        'NUMERO':
        '𝗡𝗨𝗠𝗘𝗥𝗢',
        'FECHA':
        '𝗙𝗘𝗖𝗛𝗔',
        '00:00:00':
        '𝗛𝗢𝗨𝗥',
        'ACTIVACIÓN':
        '𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗢',
        'FECHA ACTIVACIÓN':
        '𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗢',
        'ACTUALIZACION':
        '𝗩𝗜𝗚𝗘𝗡𝗧𝗘',
        'TIPO':
        '𝗖𝗟𝗔𝗦𝗜𝗙𝗜𝗖𝗔𝗖𝗜𝗢𝗡',
        'SEXO':
        '𝗦𝗘𝗫𝗢',
        '[#LEDER_BOT] → RENIEC ONLINE [PREMIUM]':
        '𝐑𝐄𝐍𝐈𝐄𝐂 𝐎𝐍𝐋𝐈𝐍𝐄 | #ℙ𝕀𝕊𝕃𝕃𝕀ℕ𝔾𝔻𝕆𝕏𝔹𝕆𝕋 \n━━━━━━━━━━━━━━━━━━',
        '**[🩸]':
        '━━━━━━━━━━━━━━━━━━',
        'FALLECIMIENTO':
        '𝗗𝗘𝗙𝗨𝗡𝗖𝗜𝗢𝗡',
        '[⛔] ANTI-SPAM ESPERA 10 SEGUNDOS.':
        '',
        '[📅] NACIMIENTO':
        '[📅] 𝗡𝗔𝗖𝗜𝗠𝗜𝗘𝗡𝗧𝗢',
        'NACIMIENTO':
        '𝗡𝗔𝗖𝗜𝗠𝗜𝗘𝗡𝗧𝗢',
        'FALLECIMIENTO':
        '𝗗𝗘𝗙𝗨𝗡𝗖𝗜𝗢𝗡',
        'DEPARTAMENTO':
        '𝗗𝗘𝗣𝗔𝗥𝗧𝗔𝗠𝗘𝗡𝗧𝗢',
        'PROVINCIA':
        '𝗣𝗥𝗢𝗩𝗜𝗡𝗖𝗜𝗔',
        'DISTRITO':
        '𝗗𝗜𝗦𝗧𝗥𝗜𝗧𝗢',
        'GRADO INSTRUCCION':
        '𝗘𝗦𝗧𝗨𝗗𝗜𝗢𝗦',
        'ESTATURA':
        '𝗔𝗟𝗧𝗨𝗥𝗔',
        'INSCRIPCION':
        '𝗜𝗡𝗦𝗖𝗥𝗜𝗣𝗖𝗜𝗢𝗡',
        'EMISION':
        '𝗘𝗠𝗜𝗦𝗜𝗢𝗡',
        'CADUCIDAD':
        '𝗖𝗔𝗗𝗨𝗖𝗜𝗗𝗔𝗗',
        'PADRE':
        '𝗣𝗔𝗗𝗥𝗘',
        'MADRE':
        '𝗠𝗔𝗗𝗥𝗘 ',
        '[🔅] UBIGEO':
        '[🌐] 𝗨𝗕𝗜𝗚𝗘𝗢',
        'RESULTADOS 𝗦𝗔𝗟𝗔𝗥𝗜𝗢S':
        '💶 | 𝗥𝗘𝗦𝗨𝗟𝗧𝗔𝗗𝗢 𝗦𝗔𝗟𝗔𝗥𝗜𝗢',
        '[#LEDER_BOT] → TELEFONOS [PREMIUM]':
        '☎️ | 𝗢𝗦𝗜𝗣𝗧𝗘𝗟 𝗢𝗡𝗟𝗜𝗡𝗘\n━━━━━━━━━━━━━━━━━━',
        '[#LEDER_BOT] → TELEFONOS [FREE]':
        '☎️ | 𝗕𝗔𝗦𝗘 𝗢𝗦𝗜𝗣𝗧𝗘𝗟\n━━━━━━━━━━━━━━━━━━',
        '[#LEDER_BOT] → TRABAJOS [PREMIUM]':
        '💼 | 𝗛𝗜𝗦𝗧𝗢𝗥𝗜𝗔𝗟 𝗖𝗛𝗔𝗠𝗕𝗔\n━━━━━━━━━━━━━━━━━━',
        '[#LEDER_BOT] → FAMILIA [PREMIUM]':
        '🌱 | 𝗥𝗔𝗠𝗔 \n━━━━━━━━━━━━━━━━━━',
        '[#LEDER_BOT] → SUELDOS [PREMIUM]':
        '💶 | 𝗛𝗜𝗦𝗧𝗢𝗥𝗜𝗔𝗟 𝗦𝗔𝗟𝗔𝗥𝗜𝗔𝗟\n━━━━━━━━━━━━━━━━━━',
        '[#LEDER_BOT] → SUNEDU [PREMIUM]':
        '🎓 | 𝗧𝗜𝗧𝗨𝗟𝗢𝗦 𝗨𝗡𝗜\n━━━━━━━━━━━━━━━━━━',
        '[#LEDER_BOT] → ARBOL GENEALOGICO [PREMIUM]':
        '🌲 | 𝗔𝗥𝗕𝗢𝗟 𝗚𝗘𝗡𝗘𝗔𝗟𝗢𝗚𝗜𝗖𝗢\n━━━━━━━━━━━━━━━━━━',
        '[#LEDER_BOT] → MOVIMIENTOS MIGRATORIOS ONLINE [PREMIUM]':
        '🛂 | 𝗠𝗢𝗩𝗜𝗠𝗜𝗘𝗡𝗧𝗢𝗦 𝗠𝗜𝗚𝗥𝗔𝗧𝗢𝗥𝗜𝗢𝗦\n━━━━━━━━━━━━━━━━━━',
        '[#JUPYTER_BOT] → CAPTURA[YAPE]':
        '🟣 | 𝗖𝗔𝗣𝗧𝗨𝗥𝗔 𝗬𝗔𝗣𝗘\n━━━━━━━━━━━━━━━━━━',
        'RESULTADOS SUELDOS': '💼 | 𝗛𝗜𝗦𝗧𝗢𝗥𝗜𝗔𝗟 𝗦𝗔𝗟𝗔𝗥𝗜𝗔𝗟',
        'RESULTADOS TRABAJOS': '💼 | 𝗛𝗜𝗦𝗧𝗢𝗥𝗜𝗔𝗟 𝗖𝗛𝗔𝗠𝗕𝗔𝗦',
        '[#LEDER_BOT] → RENIEC NOMBRES [PREMIUM]':
        '😶‍🌫️ | NOMBRES\n━━━━━━',
        '[#LEDER_BOT] → 𝗣𝗟𝗔𝗖𝗔S [PREMIUM]':
        '🚗 | 𝗣𝗟𝗔𝗖𝗔𝗦\n━━━━━━━━━━━━━━━━━━',
        '[#LEDER_BOT] → CORREOS [PREMIUM]':
        '📩 | 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗖𝗜𝗢𝗡 𝗖𝗢𝗥𝗥𝗘𝗢\n━━━━━━━━━━━━━━━━━━',
        'CORREO':
        '𝗖𝗢𝗥𝗥𝗘𝗢 ',
        'COMBUSTIBLE':
        '𝗖𝗔𝗥𝗕𝗨𝗥𝗔𝗡𝗧𝗘',
        'RESTRICCION':
        '𝗥𝗘𝗦𝗧𝗥𝗜𝗖𝗖𝗜𝗢𝗡',
        'UBIGEO RENIEC':
        '𝗨. 𝗥𝗘𝗡𝗜𝗘𝗖',
        'UBIGEO INEI':
        '𝗨. 𝗜𝗡𝗘𝗜',
        'UBIGEO SUNAT':
        '𝗨. 𝗦𝗨𝗡𝗔𝗧',
        'POSTAL':
        '𝗣𝗢𝗦𝗧𝗔𝗟',
        'NOMBRES':
        '𝗡𝗢𝗠𝗕𝗥𝗘',
        'APELLIDOS':
        '𝗔𝗣𝗘𝗟𝗟𝗜𝗗𝗢𝗦', 
        'NACIMIENTO':
        '𝗡𝗔𝗖𝗜𝗠𝗜𝗘𝗡𝗧𝗢',
        'MATRIMONIO':
        '𝗠𝗔𝗧𝗥𝗜𝗠𝗢𝗠𝗜𝗢',
        'DEFUNCION':
        '𝗗𝗘𝗙𝗨𝗡𝗖𝗜𝗢𝗡',
        'DOCUMENTO':
        '𝗗𝗡𝗜',
        'GENERO':
        '𝗚𝗘𝗡𝗘𝗥𝗢',
        'EDAD':
        '𝗘𝗗𝗔𝗗',
        '(': '' ,
        ')': '' ,
        'Se encontro':
        '',
        'VERIFICACION RELACION':
        '𝗥𝗘𝗟𝗔𝗖𝗜𝗢𝗡',
        'TIPO':
        '𝗩𝗜𝗡𝗖𝗨𝗟𝗢',
        '↞ Puedes visualizar la foto de una coincidencia gratuitamente antes de usar /dni ↠ ':
        'el diavlo, tanto se reproducen'
    }

    for old, new in replacements.items():
        message = message.replace(old, new)

    # Eliminar cualquier cosa después de "<> CONSULTADO POR:" y agregar plan_info
    message = message.split("<> CONSULTADO POR:")[0].strip()
    message += consultado_por + plan_info

    # Verifica si el mensaje contiene una palabra clave que indica un fallo
    if any(keyword in message for keyword in failed_response_keywords):
        await client.send_message(destination_chat_id,
                                  "[🚫] 𝗡𝗢 𝗛𝗔𝗬 𝗗𝗔𝗧𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦",
                                  parse_mode='markdown')
        return

    # Solo deducir créditos en la primera respuesta correcta
    original_id = original_message_data['original_id']
    if 'command' in original_message_data and original_id not in processed_commands:
        if days_remaining == "N/A" or (isinstance(days_remaining, int)
                                       and days_remaining <= 0):
            user_info['coins'] -= command_costs.get(
                original_message_data['command'], 0)
            update_user_data(original_username, user_info)
            # Marcar el comando como procesado para evitar restar créditos más de una vez
            processed_commands[original_id] = True

    # Guardar respuesta y media si existe
    pending_responses[event.message.reply_to_msg_id].append(
        (message, event.message.media))

    # Reenviar todas las respuestas acumuladas cuando se complete
    responses_to_forward = pending_responses.pop(event.message.reply_to_msg_id,
                                                 [])
    await forward_responses(destination_chat_id, responses_to_forward)


async def forward_responses(destination_chat_id, responses):
    # Si hay solo texto sin archivos, lo envia como un solo mensaje
    if all(r[1] is None for r in responses):
        combined_text = "\n\n".join([r[0] for r in responses])
        await client.send_message(destination_chat_id, combined_text)
    else:
        # Si hay archivos adjuntos, enviar cada respuesta con su adjunto respectivo
        for msg_text, media in responses:
            if media:
                await client.send_file(destination_chat_id,
                                       media,
                                       caption=msg_text)
            else:
                await client.send_message(destination_chat_id, msg_text)
            print(f"Respuesta reenviada al usuario: {msg_text}")


def get_user_data(username):
    data = load_user_data(
    )  # Cargar user_data en tiempo real cada vez que se llama esta función
    return data.get(
        username, {
            "premium_start": None,
            "premium_end": None,
            "registered": False,
            "coins": 0,
            "warnings": 0,
            "role": "NO CLIENTE",
            "anti_spam": 0,
            "queries": 0,
            "joined": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })


def get_seller_data(seller_username):
    """
    Obtiene los datos de un seller del archivo seller_data.json.
    Si el seller no existe, inicializa sus datos.
    """
    if seller_username not in seller_data:
        # Inicializar la entrada del seller si no existe
        seller_data[seller_username] = {
            "assigned_credits": 0,
            "assigned_days": 0,
            "sold_credits": [],
            "sold_days": []
        }
    return seller_data[seller_username]


def update_seller_data(seller_username, data):
    """
    Actualiza los datos de un seller en el archivo seller_data.json.
    """
    seller_data[seller_username] = data
    save_seller_data(
        seller_data)  # Guarda los datos actualizados en el archivo JSON


@client.on(events.NewMessage(pattern='/vender'))
async def vender(event):
    sender = await event.get_sender()
    sender_username = sender.username

    # Verificar si el usuario que intenta vender es un owner
    if sender_username not in owners:
        await event.reply(
            "No tienes permiso para usar este comando. Solo los owners pueden asignar créditos o días.",
            parse_mode='markdown')
        return

    # Obtener los parámetros del comando
    parts = event.message.message.split()
    if len(parts) != 4:
        await event.reply(
            "Uso incorrecto. Uso correcto: /vender <cantidad> d|m @usuario",
            parse_mode='markdown')
        return

    try:
        cantidad = int(parts[1])
    except ValueError:
        await event.reply(
            "Cantidad inválida. Por favor, ingresa un número válido.",
            parse_mode='markdown')
        return

    unidad = parts[2].lower()
    target_seller = parts[3].lstrip('@')

    # Cargar los datos del JSON en tiempo real
    sellers = load_seller_data(
    )  # Asegúrate de tener esta función para cargar los datos del JSON

    # Verificar si el usuario objetivo es un seller
    if target_seller not in sellers:
        await event.reply("El usuario objetivo no es un seller válido.",
                          parse_mode='markdown')
        return

    # Obtener datos del seller
    seller_data_entry = get_seller_data(target_seller)

    if unidad == 'm':  # Asignar créditos al seller
        seller_data_entry['assigned_credits'] += cantidad
        await event.reply(
            f"Se han asignado {cantidad} créditos a @{target_seller} exitosamente.",
            parse_mode='markdown')
    elif unidad == 'd':  # Asignar días al seller
        seller_data_entry['assigned_days'] += cantidad
        await event.reply(
            f"Se han asignado {cantidad} días a @{target_seller} exitosamente.",
            parse_mode='markdown')
    else:
        await event.reply(
            "Unidad desconocida. Usa 'd' para días y 'm' para créditos.",
            parse_mode='markdown')
        return

    # Actualizar datos del seller en seller_data.json
    update_seller_data(target_seller, seller_data_entry)


@client.on(events.NewMessage(pattern='/sellersinfo'))
async def sellers_info(event):
    sender = await event.get_sender()
    sender_username = sender.username

    # Verificar si el usuario es un owner
    if sender_username not in owners:
        await event.reply(
            "No tienes permiso para usar este comando. Solo los owners pueden ver la información de los sellers.",
            parse_mode='markdown')
        return

    seller_data = load_seller_data(
    )  # Cargar los datos de los sellers en tiempo real
    response = "📊 **Información de Sellers** 📊\n\n"

    # Recorrer la información de cada seller y formatear la respuesta
    for seller, data in seller_data.items():
        response += f"👤 **Seller**: @{seller}\n"
        response += f"🔹 Créditos asignados: {data['assigned_credits']}\n"
        response += f"🔹 Días asignados: {data['assigned_days']}\n"
        response += "🔻 **Ventas de Créditos**:\n"

        # Listar todas las ventas de créditos
        for venta in data['sold_credits']:
            response += (
                f"  - Cantidad: {venta['cantidad']} | Comprador: @{venta['comprador']} | "
                f"Fecha: {venta['fecha']} | Vendido por: @{venta['vendido_por']}\n"
            )

        response += "🔻 **Ventas de Días**:\n"

        # Listar todas las ventas de días
        for venta in data['sold_days']:
            response += (
                f"  - Cantidad: {venta['cantidad']} | Comprador: @{venta['comprador']} | "
                f"Fecha: {venta['fecha']} | Vendido por: @{venta['vendido_por']}\n"
            )
        response += "\n"  # Añadir un espacio entre cada seller para mayor claridad

    # Enviar la respuesta al usuario
    await event.reply(response, parse_mode='markdown')


async def check_expired_premium():
    """
    Verifies expired premium subscriptions for users every 24 hours.
    Sends notifications to the admin group when a user's premium access expires or is about to expire.
    """
    while True:
        try:
            # Load all user data from the JSON file
            all_data = load_user_data()
            current_date = datetime.now()

            # Iterate through each user in the data
            for username, data in all_data.items():
                # Initialize warnings if not present
                if "warnings" not in data:
                    data["warnings"] = 0

                # Get the premium end date for the user
                premium_end_date = data.get("premium_end")
                if premium_end_date:
                    parsed_premium_end_date = parse_date(premium_end_date)
                    if parsed_premium_end_date:  # Ensure the date was parsed successfully
                        # Check if the premium has expired
                        if parsed_premium_end_date <= current_date:
                            if data["warnings"] < 3:
                                # Increment warnings and notify about impending expiration
                                data["warnings"] += 1
                                notification_message = (
                                    f"⛔ 𝗔𝗩𝗜𝗦𝗢: El acceso premium de @{username} expirará pronto. "
                                    f"Se ha enviado una advertencia ({data['warnings']}/3)."
                                )
                            else:
                                # Premium has fully expired; reset premium data
                                data["premium_start"] = None
                                data["premium_end"] = None
                                update_user_data(
                                    username, data)  # Save updated user data
                                notification_message = (
                                    f"⛔ 𝗔𝗩𝗜𝗦𝗢: 𝗘𝗟 𝗔𝗖𝗖𝗘𝗦𝗢 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗗𝗘 @{username} 𝗛𝗔 𝗘𝗫𝗣𝗜𝗥𝗔𝗗𝗢."
                                )

                            # Send notification to the admin group
                            try:
                                await client.send_message(
                                    notification_chat_id, notification_message)
                            except PeerIdInvalidError:
                                print(
                                    f"Error: No se puede enviar un mensaje al grupo {notification_chat_id}. "
                                    "Verifica que el peer sea válido.")
                            except ValueError as e:
                                print(f"Error al obtener la entidad: {e}")

            # Save all changes back to the user data file
            save_user_data(all_data)

        except Exception as e:
            # Catch unexpected errors and log them
            print(f"Error inesperado en check_expired_premium: {e}")

        # Wait 24 hours before checking again
        await asyncio.sleep(86400)


@client.on(events.NewMessage(pattern='/banprivg'))
async def handle_banprivg(event):
    sender = await event.get_sender()
    if sender.username in owner_username:
        global banpriv
        banpriv = True
        await event.reply(
            "✅ `banpriv` activado. El bot no responderá a nadie en privado excepto a los administradores."
        )
    else:
        await event.reply("❌ No tienes permisos para usar este comando.")


@client.on(events.NewMessage(pattern='/unbanprivg'))
async def handle_unbanprivg(event):
    sender = await event.get_sender()
    if sender.username in owner_username:
        global banpriv
        banpriv = False
        await event.reply(
            "✅ `banpriv` desactivado. El bot responderá normalmente en privado."
        )
    else:
        await event.reply("❌ No tienes permisos para usar este comando.")


private_command_count = defaultdict(int)

# Tiempo de espera para el antispam (15 segundos)
PRIVATE_COMMAND_COOLDOWN = timedelta(seconds=15)

# Diccionario para registrar el tiempo del último comando de cada usuario en privado para antispam
private_command_timestamps = {}
# Lista de comandos que no se procesarán en mensajes privados y en el grupo específico
restricted_commands = ['/agv', '/seeker',
                       '/comando3']  # Añade los comandos que desees bloquear

# ID del grupo donde los comandos estarán restringidos
restricted_group_id = [
    '-1002067222552', '-1002264560346'
]  # Reemplaza con los IDs de los grupos que desees restringir


@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handle_private_message(event):
    sender = await event.get_sender()
    username = sender.username or str(sender.id)

    # Verificar el estado de `banpriv`
    global banpriv
    if banpriv and sender.username not in owner_username:
        # No responder a nadie en privado excepto a los administradores
        return
    # Evitar procesamiento duplicado para el mismo mensaje
    if event.id in original_messages:
        print(f"Mensaje ya procesado: {event.id}")
        return

    # Obtener el texto del mensaje
    message_text = event.message.message.strip()
    if not message_text:
        await event.reply(
            "El mensaje no contiene un comando válido. Por favor, intenta de nuevo."
        )
        return

    # Obtener el comando
    command = message_text.split()[0]

    # Manejo de comandos internos (no reenviar a leovidal)
    if command in non_forward_commands:
        print(
            f"Comando interno detectado: {command}, manejado por el bot localmente."
        )
        await handle_special_commands(event, command)
        return

    # Verificar si el comando debe ser traducido
    if command in command_translation:
        translated_command = command_translation[command]
        message = message_text.replace(command, translated_command, 1)

    # Aplicar antispam
    is_spam = await handle_antispam(event, username)
    if is_spam:
        return  # Detener si el antispam está activo

    # Manejo de créditos o planes premium
    user_data = get_user_data(username)
    premium_end = user_data.get("premium_end")
    has_premium = premium_end and parse_date(premium_end) > datetime.now()

    if not has_premium and user_data['coins'] <= 0:
        await event.reply(
            "[⛔] 𝗡𝗢 𝗧𝗜𝗘𝗡𝗘𝗦 𝗨𝗡 𝗣𝗟𝗔𝗡 𝗢 𝗦𝗨𝗙𝗜𝗖𝗜𝗘𝗡𝗧𝗘𝗦 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 𝗣𝗔𝗥𝗔 𝗨𝗦𝗔𝗥 𝗟𝗢𝗦 𝗖𝗢𝗠𝗔𝗡𝗗𝗢 𝗗𝗘𝗟 𝗕𝗢𝗧. 𝗥𝗘𝗖𝗔𝗥𝗚𝗔 𝗖𝗢𝗡 𝗟𝗢𝗦 𝗦𝗘𝗟𝗟𝗘𝗥 𝗗𝗘 𝗔𝗕𝗔𝗝𝗢.",
            buttons=[[Button.url("☀️ 𝗔𝗞𝗗𝗜𝗢𝗦", "https://t.me/AKdios")],
                     [Button.url("🌩 𝗢𝗞𝗔𝗥𝗨𝗡", "https://t.me/OKARUN_7")],
                     [
                         Button.url("🧬 𝗚𝗥𝗨𝗣𝗢 𝗢𝗙𝗜𝗖𝗜𝗔𝗟",
                                    "https://t.me/+MPa0oFwz_fgwM2Fh")
                     ], [Button.inline("💶 𝗩𝗘𝗥 𝗣𝗥𝗘𝗖𝗜𝗢𝗦", b"ver_precios")]],
            parse_mode='markdown')
        return

    # Enviar el comando traducido a leovidal
    try:
        # Obtener la entidad del bot de destino
        entity = await client.get_input_entity(leo_vidal_username)

        if event.message.media:
            # Si hay multimedia, enviar con archivo adjunto
            media = await client.download_media(event.message.media)
            sent_message = await client.send_file(entity,
                                                  media,
                                                  caption=message)
        else:
            # Si no hay multimedia, enviar solo texto
            sent_message = await client.send_message(entity, message)

        # Incrementar el contador de consultas
        user_data["queries"] += 1
        update_user_data(username, user_data)  # Guardar los datos actualizados

        # Registrar el mensaje original para evitar duplicados
        original_messages[sent_message.id] = {
            'original_id': event.message.id,
            'original_chat_id': event.chat_id,
            'original_username': sender.username,
            'original_user_id': sender.id,
            'command': command
        }
        print(
            f"Mensaje enviado a leovidal. Usuario: {username}, Comando: {command}"
        )

    except Exception as ex:
        # Manejo de errores al enviar el mensaje
        print(f"Error enviando el mensaje a leovidal: {ex}")

    # Actualizar el tiempo y contador de comandos
    last_command_timestamps[username] = datetime.now()
    command_count[username] += 1

    # Resetear el contador si ha alcanzado el límite
    if command_count[username] >= COMMAND_LIMIT:
        command_count[username] = 0


@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_group))
async def handle_group_message(event):
    sender = await event.get_sender()
    username = sender.username
    group_id = str(event.chat_id)

    # Obtener el comando del mensaje
    command = event.message.message.split()[0]

    # Ignorar el comando si está en uno de los grupos restringidos y está en la lista de comandos restringidos
    if group_id in restricted_group_id and command in restricted_commands:
        return  # No hacer nada y salir de la función

    # Aplicar antispam si es necesario
    is_spam = await handle_antispam(event, username)
    if is_spam:
        return  # Si el antispam está activo, no procesar el comando

    # Verificar si el grupo está activo
    active_groups = load_active_groups()
    if group_id not in active_groups:
        if sender.username and sender.username == owner_username and event.message.message.startswith(
                '/activate'):
            active_groups[group_id] = True
            save_active_groups(active_groups)
            await event.reply("✅ El bot ha sido activado en este grupo.",
                              parse_mode='markdown')
        return

    if global_ban_status["group_ban"]:
        return

    # Procesar el comando si el usuario tiene un plan premium activo
    if command in non_forward_commands:
        await handle_special_commands(event, command)
    else:
        if command in command_translation:
            translated_command = command_translation[command]
            message = event.message.message.replace(command,
                                                    translated_command, 1)

            # Verificar si el usuario tiene suficientes créditos o es premium
            user_data = get_user_data(sender.username or "")
            premium_end = user_data.get("premium_end")
            has_premium = premium_end is not None and parse_date(
                premium_end) > datetime.now()
            if command in command_costs:
                cost = command_costs[command]
                if sender.username not in owners and not has_premium and user_data[
                        'coins'] < cost:
                    await event.reply(
                        "[⛔] 𝗡𝗢 𝗧𝗜𝗘𝗡𝗘𝗦 𝗨𝗡 𝗣𝗟𝗔𝗡 𝗢 𝗦𝗨𝗙𝗜𝗖𝗜𝗘𝗡𝗧𝗘𝗦 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 𝗣𝗔𝗥𝗔 𝗨𝗦𝗔𝗥 𝗟𝗢𝗦 𝗖𝗢𝗠𝗔𝗡𝗗𝗢 𝗗𝗘𝗟 𝗕𝗢𝗧. 𝗥𝗘𝗖𝗔𝗥𝗚𝗔 𝗖𝗢𝗡 𝗟𝗢𝗦 𝗦𝗘𝗟𝗟𝗘𝗥 𝗗𝗘 𝗔𝗕𝗔𝗝𝗢.",
                        buttons=[
                            [Button.url("☀️ 𝗔𝗞𝗗𝗜𝗢𝗦", "https://t.me/AKdios")],
                            [Button.url("🌩 𝗢𝗞𝗔𝗥𝗨𝗡", "https://t.me/OKARUN_7")],
                            [
                                Button.url("🧬 𝗚𝗥𝗨𝗣𝗢 𝗢𝗙𝗜𝗖𝗜𝗔𝗟",
                                           "https://t.me/+MPa0oFwz_fgwM2Fh")
                            ],
                            [Button.inline("💶 𝗩𝗘𝗥 𝗣𝗥𝗘𝗖𝗜𝗢𝗦", b"ver_precios")]
                        ],
                        parse_mode='markdown')
                    return

            try:
                # Preparar el mensaje
                entity = await client.get_input_entity(leo_vidal_username)
                # Descargar archivos si los hay
                downloaded_files = []
                if event.message.media:
                    media_type = type(event.message.media)

                    # Descargar imágenes (solo imágenes jpg, png, etc.)
                    if media_type in (telethon.tl.types.MessageMediaPhoto,
                                      telethon.tl.types.MessageMediaDocument):
                        file_path = await client.download_media(
                            event.message.media)
                        downloaded_files.append(file_path)

                # Enviar mensaje al bot de origen (con o sin archivos adjuntos)
                if downloaded_files:
                    await client.send_file(entity,
                                           downloaded_files,
                                           caption=message)
                else:
                    sent_message = await client.send_message(entity, message)

                # Almacenar información del mensaje original
                original_messages[sent_message.id] = {
                    'original_id': event.message.id,
                    'original_chat_id': event.chat_id,
                    'original_username': sender.username,
                    'command': command
                }

            except Exception as ex:
                await event.reply(f"Error enviando el mensaje: {ex}",
                                  parse_mode='markdown')

            # Limpiar archivos descargados
            for file_path in downloaded_files:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error al eliminar el archivo {file_path}: {e}")

    # Actualizar el tiempo y contador de comandos
    last_command_timestamps[username] = datetime.now()
    command_count[username] += 1

    # Resetear el contador si ha alcanzado el límite
    if command_count[username] >= COMMAND_LIMIT:
        command_count[username] = 0


# Ruta del archivo donde se guardarán los datos básicos de los usuarios
id_file = 'id.json'


# Función para cargar los datos del archivo id.json
def load_id_data():
    try:
        with open(id_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Función para guardar los datos en id.json
def save_id_data(data):
    with open(id_file, 'w') as f:
        json.dump(data, f, indent=4)


# Función para actualizar los datos de un usuario en id.json
def update_id_data(user_id, data):
    all_data = load_id_data()
    all_data[user_id] = data
    save_id_data(all_data)


# Función para obtener los datos de un usuario
def get_id_data(user_id):
    data = load_id_data()
    return data.get(str(user_id))  # Usar user_id como cadena para consistencia


@client.on(events.NewMessage(func=lambda e: e.is_group))
async def capture_basic_info(event):
    sender = await event.get_sender()
    user_id = sender.id
    first_name = sender.first_name
    last_name = sender.last_name if sender.last_name else ""
    username = sender.username if sender.username else "Sin username"

    # Cargar datos actuales de id.json y user_data.json
    id_data = get_id_data(user_id) or {}  # Datos básicos del usuario
    user_data = get_user_data(username) or {}  # Datos extendidos del usuario

    # Variables para controlar si hubo cambios
    updated = False

    # Verificar cambios en id.json
    if id_data.get("first_name") != first_name or id_data.get(
            "last_name") != last_name or id_data.get("username") != username:
        id_data.update({
            "id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username
        })
        update_id_data(user_id, id_data)  # Guardar cambios en id.json
        updated = True

    # Verificar cambios en user_data.json
    if user_data.get("first_name") != first_name or user_data.get(
            "last_name") != last_name or user_data.get("username") != username:
        user_data.update({
            "id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username
        })
        update_user_data(username,
                         user_data)  # Guardar cambios en user_data.json
        updated = True

    # Notificar al grupo si hubo actualizaciones
    if updated:
        message = f"""
🗂️ | 𝗗𝗔𝗧𝗢𝗦 𝗖𝗔𝗣𝗧𝗨𝗥𝗔𝗗𝗢𝗦:

⌞ 𝗜𝗗: {user_id}
⌞ 𝗡𝗢𝗠𝗕𝗥𝗘: {first_name} {last_name}
⌞ 𝗨𝗦𝗨𝗔𝗥𝗜𝗢: @{username if username != "Sin username" else "Sin username"}
"""
        await event.reply(message, parse_mode='markdown')
    else:
        print(
            f"Usuario {first_name} {last_name} (ID: {user_id}) ya estaba actualizado."
        )


# Manejo del callback para ver precios
@client.on(events.CallbackQuery(data=b"ver_precios"))
async def show_prices(event):
    buy_text = """
    🇵🇪 𝗣𝗥𝗘𝗖𝗜𝗢𝗦 #ℙ𝕀𝕊𝕃𝕃𝕀ℕ𝔾_𝔻𝕆𝕏
「 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 𝗬 𝗣𝗟𝗔𝗡𝗘𝗦 」🇵🇪

➥ 𝗣𝗥𝗘𝗖𝗜𝗢 𝗗𝗘 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦

🔖 𝟯𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟳 𝗦𝗢𝗟𝗘𝗦
🔖 𝟭𝟭𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟭𝟮 𝗦𝗢𝗟𝗘𝗦
🔖 𝟮𝟴𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟮𝟮 𝗦𝗢𝗟𝗘𝗦
🔖 𝟰𝟱𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟯𝟱 𝗦𝗢𝗟𝗘𝗦
🔖 𝟱𝟵𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟰𝟱 𝗦𝗢𝗟𝗘𝗦
🔖 𝟭𝟱𝟬𝟬 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦 ➥ 𝟵𝟬 𝗦𝗢𝗟𝗘𝗦

➥ 𝗣𝗥𝗘𝗖𝗜𝗢 𝗗𝗘 𝗣𝗟𝗔𝗡𝗘𝗦 𝗜𝗟𝗜𝗠𝗜𝗧𝗔𝗗𝗢

🎯 𝟳 𝗗𝗜𝗔𝗦 ➥ 𝟭𝟬 𝗦𝗢𝗟𝗘𝗦
🎯 𝟭𝟱 𝗗𝗜𝗔𝗦 ➥ 𝟮𝟬 𝗦𝗢𝗟𝗘𝗦
🎯 𝟯𝟬 𝗗𝗜𝗔𝗦 ➥ 𝟰𝟬 𝗦𝗢𝗟𝗘𝗦
🎯 𝟲𝟬 𝗗𝗜𝗔𝗦 ➥ 𝟳𝟱 𝗦𝗢𝗟𝗘𝗦

📣 𝗡𝗨𝗘𝗦𝗧𝗥𝗢 𝗕𝗢𝗧 𝗡𝗢 𝗧𝗜𝗘𝗡𝗘 𝗥𝗔𝗡𝗚𝗢𝗦,  𝗣𝗢𝗗𝗥𝗔𝗦 𝗔𝗖𝗖𝗘𝗗𝗘𝗥 𝗔 𝗟𝗢𝗦 𝗖𝗢𝗠𝗔𝗡𝗗𝗢𝗦 𝗦𝗜𝗡 𝗥𝗘𝗦𝗧𝗥𝗜𝗖𝗖𝗜𝗢𝗡, 𝗬𝗔 𝗦𝗘𝗔 𝗤𝗨𝗘 𝗖𝗢𝗠𝗣𝗥𝗘𝗦 𝗗𝗜𝗔𝗦 𝗢 𝗖𝗥𝗘𝗗𝗜𝗧𝗢𝗦.

➥ 𝗩𝗘𝗡𝗗𝗘𝗗𝗢𝗥𝗘𝗦 𝗢𝗙𝗜𝗖𝗜𝗔𝗟𝗘𝗦 ⬎
    """

    buttons = [[Button.url("☀️ 𝗔𝗞𝗗𝗜𝗢𝗦 ", "https://t.me/AKdios")],
               [Button.url("🌩 𝗢𝗞𝗔𝗥𝗨𝗡", "https://t.me/OKARUN_7")]]
    await event.edit(buy_text, buttons=buttons, parse_mode='markdown')


iniciar_manejador_id(client)
iniciar_comando_calificar(client)
iniciar_comando_ver_calificacion(client)
iniciar_comando_donar(client)
registrar_comando_fake(client)


async def main():
    # Iniciar sesión en el cliente utilizando el bot token
    await client.start(bot_token=bot_token)

    asyncio.create_task(check_expired_premium())

    await client.run_until_disconnected()




    asyncio.run(main())
