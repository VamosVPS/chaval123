import requests
from geopy.geocoders import Nominatim
from faker import Faker
import logging

logging.basicConfig(filename='bot.log', level=logging.INFO)

# Inicializar Nominatim para obtener direcciones
geolocator = Nominatim(user_agent="bot_direcciones")

# Inicializar Faker para generar nombres y datos aleatorios
fake = Faker()

# Generar un correo temporal usando la API de 1secmail (no necesita API key)
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

# Obtener dirección real usando Nominatim (OpenStreetMap)
def obtener_direccion_real(pais):
    try:
        location = geolocator.geocode(pais, exactly_one=True)
        if location:
            address = location.address
            ciudad = location.raw.get('address', {}).get('city', 'Datos no disponibles')
            region = location.raw.get('address', {}).get('state', 'Datos no disponibles')
            
            return {
                "direccion": address,
                "ciudad": ciudad,
                "region": region,
                "latitud": location.latitude,
                "longitud": location.longitude,
                "nombre": fake.first_name(),
                "apellido": fake.last_name(),
                "telefono": generar_telefono_aleatorio(pais)
            }
        else:
            logging.warning(f"No se encontró dirección para el país: {pais}")
            return {
                "direccion": "Datos no disponibles",
                "ciudad": "Datos no disponibles",
                "region": "Datos no disponibles",
                "latitud": "N/A",
                "longitud": "N/A",
                "nombre": fake.first_name(),
                "apellido": fake.last_name(),
                "telefono": "Desconocido"
            }
    except Exception as e:
        logging.error(f"Error al obtener dirección de Nominatim: {e}")
        return {
            "direccion": "Datos no disponibles",
            "ciudad": "Datos no disponibles",
            "region": "Datos no disponibles",
            "latitud": "N/A",
            "longitud": "N/A",
            "nombre": fake.first_name(),
            "apellido": fake.last_name(),
            "telefono": "Desconocido"
        }

# Función para generar teléfonos aleatorios basados en el país
def generar_telefono_aleatorio(pais):
    if pais.lower() == "perú":
        return "+51 9" + str(fake.random_number(digits=8))
    elif pais.lower() == "méxico":
        return "+52 1" + str(fake.random_number(digits=8))
    elif pais.lower() == "estados unidos":
        return "+1 " + str(fake.random_number(digits=10))
    else:
        return "+00 " + str(fake.random_number(digits=10))
