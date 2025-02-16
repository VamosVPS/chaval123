import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Función para ejecutar Selenium y verificar el operador
def verificar_operador(numero_telefono):
    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    edge_options.add_argument('--disable-gpu')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')
    edge_options.add_argument('--headless')  # Modo headless para hacerlo más rápido

    edge_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    service = EdgeService('C:/Users/githu/OneDrive/Desktop/a/msedgedriver.exe')
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        driver.get('https://www.ding.com/es/paises/america-del-sur/peru')

        # Cerrar el banner de cookies si aparece
        try:
            cookies_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
            )
            cookies_button.click()
            print("Banner de cookies cerrado.")
        except:
            print("No se encontró el banner de cookies o no es necesario cerrarlo.")

        # Introducir el número de teléfono y verificar el operador
        telefono_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Introduce el número de teléfono']"))
        )
        telefono_input.send_keys(numero_telefono)

        boton_recarga = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='button-country-widget']"))
        )
        boton_recarga.click()

        lapiz_editar = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-testid='summary-product-edit-button']"))
        )
        lapiz_editar.click()

        operador_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-testid='summary-operator-content-value-typography']"))
        )
        operador = operador_element.text.strip()
        return operador

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()

# Función asincrónica para usar con el bot
async def verificar_operador_async(numero_telefono):
    # Ejecutar la función en un hilo separado para no bloquear el bot
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        operador = await loop.run_in_executor(pool, verificar_operador, numero_telefono)
    return operador

# Función para manejar el comando del bot
async def handle_vernum_command(event):
    numero_telefono = event.message.text.split()[1]  # Extraer el número del comando

    # Enviar un mensaje mientras se procesa la solicitud
    await event.reply(f"Consultando operador para el número {numero_telefono}...")

    # Llamar a la función para verificar el operador de forma asíncrona
    operador = await verificar_operador_async(numero_telefono)

    if operador:
        await event.reply(f"El operador detectado para el número {numero_telefono} es {operador}.")
    else:
        await event.reply(f"No se pudo determinar el operador para el número {numero_telefono}.")

