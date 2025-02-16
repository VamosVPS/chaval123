import time
import random
import base64
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

# Función para guardar la imagen del CAPTCHA en un archivo
def guardar_imagen_base64(base64_str, nombre_archivo):
    # Decodificar el string base64 y guardar como imagen PNG
    imagen_data = base64.b64decode(base64_str.split(',')[1])
    with open(nombre_archivo, 'wb') as f:
        f.write(imagen_data)
    print(f"Imagen guardada como {nombre_archivo}")

# Función para enviar el CAPTCHA a Bing Copilot
def resolver_captcha_con_copilot(driver):
    # Abrir nueva pestaña y dirigirse a Microsoft Copilot
    driver.execute_script("window.open('https://copilot.microsoft.com', '_blank');")
    driver.switch_to.window(driver.window_handles[1])  # Cambiar a la nueva pestaña de Copilot

    try:
        # Esperar a que la página cargue
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Escribir el prompt en el textarea de Copilot
        prompt = "Te mandaré una imagen, solo dime el CAPTCHA que aparece en ella, solo los 6 dígitos."
        textarea = driver.find_element(By.ID, 'userInput')
        textarea.send_keys(prompt)

        # Adjuntar la imagen del CAPTCHA (ruta al archivo que ya se descargó antes)
        boton_adjuntar_imagen = driver.find_element(By.XPATH, '//input[@type="file"]')
        boton_adjuntar_imagen.send_keys('C:/ruta/a/captcha_sunarp.png')  # Cambia por la ruta del archivo guardado

        # Pausa antes de enviar el mensaje
        time.sleep(2)

        # Hacer clic en el botón de enviar mensaje
        boton_enviar = driver.find_element(By.XPATH, '//button[@title="Enviar mensaje"]')
        boton_enviar.click()

        # Esperar la respuesta de Copilot
        respuesta_captcha = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'respuesta_clase')))  # Ajusta esto según la estructura de Copilot
        captcha_texto = respuesta_captcha.text.strip()  # Capturar y limpiar el texto
        print(f"El CAPTCHA resuelto por Copilot es: {captcha_texto}")

        # Volver a la pestaña de SUNARP
        driver.switch_to.window(driver.window_handles[0])

        return captcha_texto

    except Exception as e:
        print(f"Error al interactuar con Copilot: {e}")
        return None

# Función para consultar el vehículo en SUNARP
def consultar_vehiculo(placa):
    # Configurar el WebDriver para usar Edge (Chromium)
    edge_options = EdgeOptions()
    edge_options.use_chromium = True

    # Usar el perfil de usuario actual en 'Profile 1'
    edge_options.add_argument("--user-data-dir=C:/Users/githu/AppData/Local/Microsoft/Edge/User Data")  # Ruta al User Data
    edge_options.add_argument("--profile-directory=Profile 1")  # Usa el perfil correcto

    # Deshabilitar GPU para evitar posibles problemas gráficos
    edge_options.add_argument('--disable-gpu')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')

    # Mostrar el navegador en modo maximizado
    edge_options.add_argument('--start-maximized')

    service = EdgeService('C:/Users/githu/OneDrive/Desktop/a/msedgedriver.exe')
    driver = webdriver.Edge(service=service, options=edge_options)

    intentos = 0
    max_intentos = 10  # Máximo de intentos para resolver el CAPTCHA
    captcha_valido = False

    while intentos < max_intentos and not captcha_valido:
        try:
            # Abrir la página de consulta vehicular de SUNARP
            driver.get('https://www2.sunarp.gob.pe/consulta-vehicular/inicio')

            # Esperar a que el campo de la placa sea interactivo
            placa_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'nroPlaca'))
            )
            
            # Introducir la placa
            placa_input.clear()
            time.sleep(random.uniform(1, 2))  # Pausa antes de escribir la placa
            placa_input.send_keys(placa)

            # Pausa deliberada para simular la interacción humana
            time.sleep(random.uniform(2, 3))

            # Obtener la imagen del CAPTCHA (base64)
            captcha_element = driver.find_element(By.ID, 'image')
            captcha_base64 = captcha_element.get_attribute("src")

            # Guardar la imagen del CAPTCHA en un archivo
            guardar_imagen_base64(captcha_base64, "captcha_sunarp.png")

            # Enviar la imagen a Copilot para resolver el CAPTCHA
            captcha_texto = resolver_captcha_con_copilot(driver)

            if not captcha_texto:
                print("No se detectó correctamente un CAPTCHA válido. Intentando de nuevo...")
                intentos += 1
                continue

            # Volver a SUNARP e ingresar el CAPTCHA resuelto
            print(f"CAPTCHA detectado: {captcha_texto}")
            captcha_input = driver.find_element(By.ID, 'codigoCaptcha')
            captcha_input.clear()
            captcha_input.send_keys(captcha_texto)

            # Pausa antes de interactuar con el botón de búsqueda
            time.sleep(random.uniform(2, 3))

            # Hacer clic en el botón de búsqueda
            boton_buscar = driver.find_element(By.XPATH, '//span[contains(text(), "Realizar Busqueda")]/..')
            try:
                boton_buscar.click()
            except ElementNotInteractableException:
                # Si el botón no es interactivo, intentamos hacer scroll y luego clic
                driver.execute_script("arguments[0].scrollIntoView();", boton_buscar)
                boton_buscar.click()

            # Verificar si aparece la ventana emergente de "Captcha inválido" o "Placa no encontrada"
            try:
                mensaje_error = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'swal2-title')))
                if mensaje_error.text == "Captcha inválido":
                    print("CAPTCHA no válido, recargando...")
                    driver.find_element(By.CLASS_NAME, 'swal2-confirm').click()  # Clic en el botón OK
                    intentos += 1
                    time.sleep(2)  # Pausa antes de recargar el captcha
                elif mensaje_error.text == "No se ha encontrado la placa del vehículo ingresado":
                    print("Placa no encontrada.")
                    driver.find_element(By.CLASS_NAME, 'swal2-confirm').click()  # Clic en el botón OK
                    break
                else:
                    print("Error desconocido: ", mensaje_error.text)
                    break
            except NoSuchElementException:
                print("CAPTCHA válido y búsqueda realizada correctamente.")
                captcha_valido = True

                # Extraer los datos del vehículo
                try:
                    datos_vehiculo = driver.find_element(By.CLASS_NAME, 'contenedor_consulta').text
                    print("Datos del vehículo obtenidos:\n", datos_vehiculo)
                except NoSuchElementException:
                    print("No se pudieron extraer los datos del vehículo.")
                break

        except Exception as e:
            print(f"Error en intento {intentos + 1}: {e}")
            intentos += 1
        finally:
            if intentos == max_intentos:
                print("Número máximo de intentos alcanzado.")

    driver.quit()

# Ejecutar la función con la placa proporcionada
placa = input("Introduce la placa del vehículo: ")
consultar_vehiculo(placa)
