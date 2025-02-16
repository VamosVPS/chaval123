from faker import Faker
from api_utils import obtener_direccion_real

# Diccionario para asignar locales de Faker según el código de país
faker_locales = {
    "pe": "es_ES",  # Perú
    "us": "en_US",  # Estados Unidos
    "mx": "es_MX",  # México
    "es": "es_ES",  # España
    "ar": "es_AR",  # Argentina
    "co": "es_CO",  # Colombia
    "cl": "es_CL",  # Chile
}

# Diccionario para los nombres de los países
nombres_paises = {
    "pe": "Perú",
    "us": "Estados Unidos",
    "mx": "México",
    "es": "España",
    "ar": "Argentina",
    "co": "Colombia",
    "cl": "Chile",
}

# Función para generar un número de teléfono aleatorio por país
def generar_numero_telefono(codigo_pais):
    fake = Faker()
    if codigo_pais == "pe":
        return f"+51 9{fake.random_number(digits=8)}"  # Número de Perú
    elif codigo_pais == "us":
        return f"+1 {fake.random_number(digits=10)}"  # Número de EE.UU.
    elif codigo_pais == "mx":
        return f"+52 55{fake.random_number(digits=8)}"  # Número de México
    elif codigo_pais == "es":
        return f"+34 {fake.random_number(digits=9)}"  # Número de España
    else:
        return f"+{fake.random_number(digits=10)}"  # Número genérico

# Función para generar datos detallados
def generar_informacion_detallada(codigo_pais):
    locale = faker_locales.get(codigo_pais, 'en_US')  # Locale por defecto en_US
    fake = Faker(locale)

    nombre = fake.first_name()
    apellido = fake.last_name()
    direccion = obtener_direccion_real(nombres_paises.get(codigo_pais, "Estados Unidos"))
    
    if direccion:
        return {
            "nombre": nombre,
            "apellido": apellido,
            "direccion_real": direccion["direccion"],
            "ciudad": direccion["ciudad"],
            "region": direccion["region"],
            "latitud": direccion["latitud"],
            "longitud": direccion["longitud"],
            "telefono": generar_numero_telefono(codigo_pais),
        }
    else:
        # Si no se puede obtener una dirección, usar datos de Faker
        return {
            "nombre": nombre,
            "apellido": apellido,
            "direccion_real": f"{fake.street_address()}, {nombres_paises.get(codigo_pais, 'Estados Unidos')}",
            "ciudad": fake.city(),
            "region": fake.state(),
            "latitud": "N/A",
            "longitud": "N/A",
            "telefono": generar_numero_telefono(codigo_pais),
        }
