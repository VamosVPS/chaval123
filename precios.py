# precios.py

from datetime import datetime
import json

# Ruta del archivo JSON
FILE_PATH = "user_data.json"

def get_user_data(username, file_path=FILE_PATH):
    """
    Obtiene los datos del usuario desde el archivo JSON en tiempo real.
    
    Args:
    - username (str): El nombre de usuario para buscar en el archivo.
    - file_path (str): Ruta al archivo JSON que contiene los datos de usuario.
    
    Returns:
    - user_data (dict): Datos del usuario si existe, de lo contrario un dict vacío.
    """
    try:
        # Leer el archivo JSON en tiempo real
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get(username, {})
    except FileNotFoundError:
        # Si el archivo no existe, retornamos un dict vacío
        return {}
    except json.JSONDecodeError:
        # Si el archivo está corrupto, también devolvemos un dict vacío
        return {}

def verificar_acceso(user_data, precio_comando):
    """
    Verifica si el usuario tiene acceso a ejecutar un comando basándose en su plan o créditos.
    
    Args:
    - user_data (dict): Datos del usuario, incluyendo si tiene un plan activo y sus créditos.
    - precio_comando (int): El precio en créditos para el comando que se quiere ejecutar.
    
    Returns:
    - acceso_permitido (bool): Si el usuario tiene permiso para ejecutar el comando.
    - mensaje_error (str): Mensaje a mostrar si no tiene acceso (vacío si tiene acceso).
    """
    
    # Verificar si el usuario tiene un plan activo por días
    if tiene_plan_activo(user_data):
        # El usuario tiene un plan ilimitado activo, no es necesario gastar créditos
        return True, ""

    # Verificar si el usuario tiene suficientes créditos
    if user_data.get('coins', 0) >= precio_comando:
        return True, ""

    # Si no tiene suficientes créditos o un plan activo, denegar acceso
    return False, "No tienes suficientes créditos ni un plan activo para ejecutar este comando."

def reducir_creditos(user_data, precio_comando, username, file_path=FILE_PATH):
    """
    Reduce los créditos del usuario si no tiene un plan ilimitado activo.
    
    Args:
    - user_data (dict): Datos del usuario.
    - precio_comando (int): El precio en créditos para el comando.
    - username (str): El nombre de usuario para actualizar los datos.
    - file_path (str): Ruta al archivo JSON que contiene los datos de usuario.
    
    """
    
    # Verificar si el usuario no tiene un plan ilimitado activo
    if not tiene_plan_activo(user_data):
        # Restar los créditos del usuario
        user_data['coins'] -= precio_comando
        # Actualizar los datos del usuario en el archivo JSON
        update_user_data(username, user_data, file_path)

def parse_date(date_string):
    """
    Función para convertir una cadena de fecha a un objeto datetime.
    Se asume un formato de fecha DD/MM/YY.
    
    Args:
    - date_string (str): La cadena de fecha que debe ser convertida.
    
    Returns:
    - datetime: Objeto datetime generado a partir de la cadena.
    """
    return datetime.strptime(date_string, '%d/%m/%y')

def tiene_plan_activo(user_data):
    """
    Verifica si el usuario tiene un plan ilimitado activo por días.
    
    Args:
    - user_data (dict): Datos del usuario, incluyendo información sobre su plan premium.
    
    Returns:
    - (bool): Si el usuario tiene un plan activo o no.
    """
    # Verificar si premium_end es mayor a la fecha actual
    if user_data.get("premium_end"):
        fecha_fin = parse_date(user_data["premium_end"])
        if fecha_fin > datetime.now():
            return True
    return False

def update_user_data(username, user_data, file_path=FILE_PATH):
    """
    Actualiza los datos del usuario en el archivo JSON.
    
    Args:
    - username (str): Nombre de usuario que será actualizado.
    - user_data (dict): Los datos actualizados del usuario.
    - file_path (str): Ruta al archivo JSON que contiene los datos de usuario.
    """
    try:
        # Cargar los datos actuales del archivo JSON
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Actualizar los datos del usuario
        data[username] = user_data

        # Guardar los cambios en el archivo JSON
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error al actualizar los datos del usuario: {e}")

def verificar_registrado(user_data):
    """
    Verifica si el usuario está registrado.
    
    Args:
    - user_data (dict): Datos del usuario.
    
    Returns:
    - (bool): Si el usuario está registrado.
    """
    return user_data.get('registered', False)

def obtener_creditos(user_data):
    """
    Retorna la cantidad de créditos que tiene el usuario.
    
    Args:
    - user_data (dict): Datos del usuario, incluyendo la cantidad de créditos.
    
    Returns:
    - (int): El número de créditos que tiene el usuario.
    """
    return user_data.get('coins', 0)
