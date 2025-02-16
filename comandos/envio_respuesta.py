from telethon import events
import asyncio

async def enviar_y_esperar_respuesta(client, destinatario, mensaje, timeout=30):
    """
    Envía un mensaje a un destinatario y espera su respuesta.

    Args:
        client (TelegramClient): La instancia del cliente de Telethon.
        destinatario (str): Nombre de usuario o ID del destinatario.
        mensaje (str): El mensaje a enviar.
        timeout (int): Tiempo máximo para esperar una respuesta (en segundos).

    Returns:
        str: La respuesta recibida.

    Raises:
        TimeoutError: Si no se recibe respuesta dentro del tiempo especificado.
        Exception: Otros errores relacionados con el envío/recepción.
    """
    # Evento para capturar la respuesta
    response_event = asyncio.Event()
    respuesta = None

    async def handle_response(event):
        nonlocal respuesta
        if event.sender.username == destinatario:
            respuesta = event.raw_text
            response_event.set()

    # Registrar el manejador temporal
    client.add_event_handler(handle_response, events.NewMessage(from_users=destinatario))

    try:
        # Enviar el mensaje al destinatario
        await client.send_message(destinatario, mensaje)

        # Esperar la respuesta o el timeout
        await asyncio.wait_for(response_event.wait(), timeout=timeout)

        # Devolver la respuesta capturada
        return respuesta
    except asyncio.TimeoutError:
        raise TimeoutError(f"No se recibió respuesta de {destinatario} en {timeout} segundos.")
    except Exception as e:
        raise e
    finally:
        # Eliminar el manejador temporal
        client.remove_event_handler(handle_response, events.NewMessage(from_users=destinatario))
