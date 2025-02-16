import json
import logging
from datetime import datetime, timedelta
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

# Función para donar coins o días de premium
def donar(usuario_donante, usuario_destinatario, cantidad, tipo, datos_usuarios):
    if usuario_donante not in datos_usuarios or usuario_destinatario not in datos_usuarios:
        return f"⚠️ Usuario {usuario_destinatario} no registrado en el sistema."

    if tipo == "coins":
        if datos_usuarios[usuario_donante]["coins"] < cantidad:
            return f"⚠️ No tienes suficientes coins para donar."
        datos_usuarios[usuario_donante]["coins"] -= cantidad
        datos_usuarios[usuario_destinatario]["coins"] += cantidad
        mensaje = f"💰 Has donado {cantidad} coins a {usuario_destinatario}."

    elif tipo == "dias":
        fecha_fin_donante = datetime.strptime(datos_usuarios[usuario_donante]["premium_end"], "%d/%m/%y")
        if (fecha_fin_donante - datetime.now()).days < cantidad:
            return f"⚠️ No tienes suficientes días de premium para donar."
        
        fecha_fin_destinatario = datetime.strptime(datos_usuarios[usuario_destinatario]["premium_end"], "%d/%m/%y")
        
        # Restar días al donante y sumarlos al destinatario
        nueva_fecha_donante = fecha_fin_donante - timedelta(days=cantidad)
        nueva_fecha_destinatario = fecha_fin_destinatario + timedelta(days=cantidad)
        
        datos_usuarios[usuario_donante]["premium_end"] = nueva_fecha_donante.strftime("%d/%m/%y")
        datos_usuarios[usuario_destinatario]["premium_end"] = nueva_fecha_destinatario.strftime("%d/%m/%y")
        mensaje = f"🎁 Has donado {cantidad} días de premium a {usuario_destinatario}."

    guardar_datos_usuarios(datos_usuarios)
    return mensaje

# Comando para donar coins o días
def iniciar_comando_donar(client):
    @client.on(events.NewMessage(pattern=r'/donar'))
    async def donar_handler(event):
        # Si el comando no tiene más parámetros, mostrar la guía de uso
        if len(event.message.text.split()) == 1:
            await event.respond(
                "📝 **Guía de uso del comando /donar**\n\n"
                "Puedes donar coins o días de premium a otro usuario con los siguientes formatos:\n"
                "1. **/donar @usuario [cantidad] coins** - Para donar coins.\n"
                "2. **/donar @usuario [cantidad] dias** - Para donar días de premium.\n"
                "3. Responde al mensaje de otro usuario con **/donar [cantidad] coins/dias** para donar directamente."
            )
            return

        # Obtener el nombre de usuario de quien está donando
        usuario_donante = event.sender.username
        
        # Verificar si es una respuesta a un mensaje
        if event.is_reply:
            usuario_destinatario = (await event.get_reply_message()).sender.username
        else:
            # Si no es respuesta, obtener el usuario del comando
            try:
                usuario_destinatario = event.message.text.split()[1].replace("@", "")
            except IndexError:
                await event.respond("⚠️ Error en el formato del comando. Asegúrate de seguir la guía de uso.")
                return

        # Obtener la cantidad y el tipo de donación
        try:
            cantidad = int(event.message.text.split()[2])
            tipo = event.message.text.split()[3].lower()  # "coins" o "dias"
        except (IndexError, ValueError):
            await event.respond("⚠️ Error en el formato del comando. Asegúrate de ingresar una cantidad válida y especificar 'coins' o 'dias'.")
            return

        # Cargar los datos de usuarios
        datos_usuarios = cargar_datos_usuarios()

        # Verificar si el usuario donante y destinatario existen y tienen suficientes coins/días
        mensaje = donar(usuario_donante, usuario_destinatario, cantidad, tipo, datos_usuarios)

        # Enviar el mensaje de confirmación o error
        await event.respond(mensaje)
