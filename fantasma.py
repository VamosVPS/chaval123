import re
import os
import io
import asyncio
from telethon import TelegramClient, events

def buscar_coincidencia_comando(dni, mensajes):
    """
    Busca coincidencias del DNI en los mensajes no respondidos directamente.
    
    Args:
    dni (str): El DNI de 8 dígitos que se va a buscar en las respuestas.
    mensajes (list): Lista de mensajes no directos que se deben analizar.
    
    Returns:
    dict: Mensaje coincidente o None si no encuentra coincidencias.
    """
    pattern = re.compile(r'\b' + re.escape(dni) + r'\b')  # Asegura coincidencia exacta de 8 dígitos

    for mensaje in mensajes:
        # Verifica si el DNI aparece en el texto del mensaje
        if pattern.search(mensaje['texto']):
            print(f"Coincidencia encontrada en el mensaje: {mensaje['texto']}")
            return mensaje  # Retorna el mensaje coincidente
    
    return None  # No se encontraron coincidencias

def procesar_pdf_y_eliminar_logo(pdf_path):
    """
    Procesa el PDF descargado y lo reenvía tal como está, sin modificar el contenido.
    
    Args:
    pdf_path (str): Ruta del PDF original.
    
    Returns:
    str: Ruta del PDF sin modificar (se devuelve el mismo archivo).
    """
    # En este caso, simplemente se devuelve el archivo PDF descargado sin modificaciones
    print(f"PDF descargado y listo para enviar: {pdf_path}")
    return pdf_path

async def forward_response(event, client, original_messages, pending_responses, target_user_username):
    """
    Maneja las respuestas del target_user_username y las reenvía como si fueran respuestas directas al comando original.
    También detecta mensajes que contienen coincidencias de DNI y los trata como respuestas directas.
    """
    print(f"Respuesta recibida del usuario de destino: {event.message.text}")
    
    # Obtener datos del mensaje original
    original_message_data = original_messages.get(event.message.reply_to_msg_id)

    # Si no hay una respuesta directa, busca coincidencias en los mensajes no respondidos
    if not original_message_data:
        # Suponemos que 'dni' es parte del mensaje o se deriva del comando
        dni = extract_dni_from_message(event.message.text)  # Función que debe extraer el DNI del mensaje
        if dni:
            coincidencia = buscar_coincidencia_comando(dni, pending_responses)

            if coincidencia:
                # Marcar el mensaje como una respuesta directa
                original_message_data = original_messages[coincidencia['original_id']]

    # Si se encuentra la coincidencia o ya es una respuesta directa, procesar el mensaje
    if original_message_data:
        destination_chat_id = original_message_data['original_chat_id']
        original_id = original_message_data['original_id']

        try:
            # Procesar texto o media según el mensaje
            if event.message.media:
                # Verificar si el mensaje tiene un archivo PDF
                if event.message.file and event.message.file.mime_type == 'application/pdf':
                    # Descargar el PDF en memoria y enviarlo
                    pdf_bytes = io.BytesIO(await event.message.download_media())
                    pdf_bytes.seek(0)  # Coloca el puntero al inicio del archivo en memoria
                    try:
                        # Enviar solo el PDF, omitiendo el texto
                        await client.send_file(destination_chat_id, pdf_bytes, reply_to=original_id)
                        print(f"PDF enviado: {event.message.file.name if event.message.file.name else 'document.pdf'}")
                    finally:
                        # Liberar la memoria después de enviar
                        pdf_bytes.close()
                else:
                    # Para otros tipos de medios, primero enviar el texto si existe
                    if event.message.text:
                        await client.send_message(destination_chat_id, event.message.text, reply_to=original_id)
                        print(f"Texto enviado: {event.message.text}")

                    # Luego enviar el medio adjunto
                    await client.send_file(destination_chat_id, event.message.media, reply_to=original_id)
                    print(f"Media enviada: {event.message.media}")

            else:
                # Si no hay media, simplemente reenvía el texto
                await client.send_message(destination_chat_id, event.message.text, reply_to=original_id)
                print(f"Mensaje reenviado: {event.message.text}")

        except Exception as e:
            print(f"Error enviando el mensaje: {e}")
    else:
        print("No se encontró mensaje original ni coincidencia de DNI.")

def extract_dni_from_message(message):
    """
    Extrae el DNI (8 dígitos) de un mensaje dado.
    
    Args:
    message (str): Texto del mensaje.
    
    Returns:
    str: DNI encontrado en el mensaje o None si no se encuentra.
    """
    match = re.search(r'\b\d{8}\b', message)  # Busca exactamente 8 dígitos
    if match:
        return match.group(0)
    return None
