from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random

def cargar_fuente(ruta_fuente, tamaño):
    """
    Carga la fuente desde una ruta especificada con el tamaño dado.
    """
    try:
        return ImageFont.truetype(ruta_fuente, tamaño)
    except IOError:
        print(f"Fuente no encontrada en {ruta_fuente}. Asegúrate de que el archivo esté presente.")
        return ImageFont.load_default()

def generar_recibo(cantidad, nombre, telefono, output_path):
    # Cargar la plantilla
    plantilla = Image.open('C:/Users/githu/OneDrive/Desktop/bot pro/yape/yap.png')  # Ruta completa al archivo

    
    # Crear objeto para dibujar
    draw = ImageDraw.Draw(plantilla)
    
    # Definir las fuentes y tamaños con rutas completas
    fuente_titulo = cargar_fuente("Roboto-Bold.ttf", 80)
    fuente_monto = cargar_fuente("Roboto-Regular.ttf", 120)
    fuente_nombre = cargar_fuente("Roboto-Regular.ttf", 50)
    fuente_fecha = cargar_fuente("Roboto-Regular.ttf", 35)
    fuente_detalle = cargar_fuente("Roboto-Regular.ttf", 40)
    
    # Obtener fecha y hora actuales
    fecha_actual = datetime.now().strftime("%d %b. %Y - %I:%M %p")
    
    # Generar número de operación aleatorio de 8 dígitos
    numero_operacion = str(random.randint(10000000, 99999999))
    
    # Coordenadas de cada campo (ajustar según la plantilla)
    coordenadas_titulo = (300, 150)
    coordenadas_monto = (300, 400)
    coordenadas_nombre = (300, 550)
    coordenadas_telefono = (300, 700)
    coordenadas_fecha = (300, 600)  
    coordenadas_numero_operacion = (300, 850)
    
    # Colocar los textos en las coordenadas especificadas
    draw.text(coordenadas_titulo, "¡Yapeaste!", font=fuente_titulo, fill="black")
    draw.text(coordenadas_monto, f"S/ {cantidad}", font=fuente_monto, fill="black")
    draw.text(coordenadas_nombre, nombre, font=fuente_nombre, fill="black")
    draw.text(coordenadas_telefono, f"*** *** {telefono[-3:]}", font=fuente_detalle, fill="black")
    draw.text(coordenadas_fecha, fecha_actual, font=fuente_fecha, fill="black")
    draw.text(coordenadas_numero_operacion, numero_operacion, font=fuente_detalle, fill="black")
    
    # Guardar la imagen generada
    plantilla.save(output_path)
    print(f"Recibo generado y guardado en {output_path}")

# Función principal para ingresar los datos manualmente
def main():
    # Solicitar datos al usuario
    cantidad = input("Ingrese la cantidad (por ejemplo, 120): ")
    nombre = input("Ingrese el nombre del destinatario (por ejemplo, Samael Dox): ")
    telefono = input("Ingrese los últimos tres dígitos del teléfono (por ejemplo, 802): ")
    
    # Ruta de salida para el recibo generado
    output_path = "recibo_generado.png"
    
    # Generar el recibo
    generar_recibo(cantidad, nombre, telefono, output_path)

if __name__ == "__main__":
    main()
