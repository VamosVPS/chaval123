from faker import Faker
from telethon import events
import requests
import logging

# Configuración del log
logging.basicConfig(filename='bot.log', level=logging.INFO)

# Diccionario para identificar el locale basado en el país
locales_por_pais = {
    "pe": "es_PE",   # Perú
    "us": "en_US",   # Estados Unidos
    "mx": "es_MX",   # México
    "es": "es_ES",   # España
    "ar": "es_AR",   # Argentina
    "co": "es_CO",   # Colombia
    "cl": "es_CL"    # Chile
}

# Genera un correo temporal usando la API de 1secmail (no necesita API key)
def generar_correo_temporal_1secmail():
    url = "https://www.1secmail.com/api/v1/?action=genRandomMailbox"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            correo = response.json()[0]
            bandeja_url = f"https://www.1secmail.com/?login={correo.split('@')[0]}&domain={correo.split('@')[1]}"
            return correo, bandeja_url
        else:
            logging.error("Error en la API de 1secmail")
            return None, None
    except Exception as e:
        logging.error(f"Error al generar correo temporal: {e}")
        return None, None

# Genera información aleatoria con Faker
def generar_informacion_falsa(codigo_pais):
    locale = locales_por_pais.get(codigo_pais, "en_US")  # Predeterminado a en_US si no se reconoce el país
    fake = Faker(locale)

    # Generar datos aleatorios
    nombre = fake.first_name()
    apellido = fake.last_name()
    direccion = fake.street_address()
    ciudad = fake.city()
    region = fake.state()
    pais = fake.current_country()
    telefono = fake.phone_number()
    latitud = fake.latitude()
    longitud = fake.longitude()

    # Empaquetar la información generada
    return {
        "nombre": nombre,
        "apellido": apellido,
        "direccion": direccion,
        "ciudad": ciudad,
        "region": region,
        "pais": pais,
        "telefono": telefono,
        "latitud": latitud,
        "longitud": longitud
    }

# Función principal que maneja la lógica del comando
async def ejecutar_comando_fake(event):
    mensaje = event.message.message.split()
    
    if len(mensaje) > 1:
        codigo_pais = mensaje[1].lower()
    else:
        codigo_pais = "us"  # Predeterminado a Estados Unidos

    # Validar el país ingresado
    if codigo_pais not in locales_por_pais:
        await event.reply("⚠️ Código de país no válido. Usa uno de los siguientes: pe, us, mx, es, ar, co, cl.")
        return

    # Generar la información aleatoria
    try:
        info = generar_informacion_falsa(codigo_pais)
        correo, bandeja_url = generar_correo_temporal_1secmail()

        if correo and bandeja_url:
            # Número de teléfono virtual (enlace a FreePhoneNum para recibir SMS)
            numero_virtual_url = "https://freephonenum.com"  # Enlace genérico a FreePhoneNum

            # Responder con los datos generados
            await event.reply(f"👤 **Nombre Generado:** {info['nombre']} {info['apellido']}\n"
                              f"🏡 **Dirección Generada:** {info['direccion']}\n"
                              f"🏙️ **Ciudad:** {info['ciudad']}\n"
                              f"🌍 **Región:** {info['region']}\n"
                              f"🇨🇴 **País:** {info['pais']}\n"
                              f"📞 **Teléfono:** {info['telefono']}\n"
                              f"🌍 **Latitud:** {info['latitud']} / **Longitud:** {info['longitud']}\n"
                              f"📧 **Correo Temporal Generado:** {correo}\n"
                              f"Consulta tu bandeja aquí: [Enlace a la bandeja de entrada]({bandeja_url})\n"
                              f"📱 **Teléfono Virtual (Para recibir SMS):** [FreePhoneNum - Servicio gratuito de SMS]({numero_virtual_url})")
        else:
            await event.reply("❌ Ocurrió un error al generar el correo temporal. Inténtalo de nuevo.")
    except Exception as e:
        logging.error(f"Error al ejecutar el comando /fake: {e}")
        await event.reply("❌ Ocurrió un error inesperado. Inténtalo más tarde.")

# Función para registrar el comando
def registrar_comando_fake(client):
    @client.on(events.NewMessage(pattern=r'/fake(\s\w{2})?'))
    async def handler_fake(event):
        await ejecutar_comando_fake(event)
