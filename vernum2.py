from fastapi import FastAPI, HTTPException
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
import uvicorn

# Inicializar FastAPI
app = FastAPI()

# Configuración del caché (TTLCache)
cache = TTLCache(maxsize=1000, ttl=300)  # Máximo de 1000 elementos, 5 minutos de TTL

# Configuración del pool de Selenium
browser_pool = ThreadPoolExecutor(max_workers=5)  # Máximo de 5 navegadores concurrentes

# Crear opciones para Edge WebDriver
def create_edge_options():
    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    edge_options.add_argument('--disable-gpu')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')
    edge_options.add_argument('--headless')
    edge_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    )
    return edge_options

# Reutilizar una instancia del navegador
def init_driver():
    service = EdgeService('C:/Users/githu/OneDrive/Desktop/a/msedgedriver.exe')
    options = create_edge_options()
    return webdriver.Edge(service=service, options=options)

# Función para ejecutar Selenium y verificar el operador
def verificar_operador(numero_telefono):
    driver = init_driver()
    try:
        driver.get('https://www.ding.com/es/paises/america-del-sur/peru')

        # Cerrar el banner de cookies si aparece
        try:
            cookies_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
            )
            cookies_button.click()
        except Exception:
            pass

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

# Función asincrónica para usar con FastAPI
async def verificar_operador_async(numero_telefono):
    if numero_telefono in cache:
        return cache[numero_telefono]

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        operador = await loop.run_in_executor(pool, verificar_operador, numero_telefono)

    if operador:
        cache[numero_telefono] = operador  # Almacenar en caché
    return operador

# Definir la ruta para consultar el operador
@app.get("/vernum/{numero_telefono}")
async def get_operador(numero_telefono: str):
    # Validar el formato del número
    if not numero_telefono.isdigit() or len(numero_telefono) < 9:
        raise HTTPException(status_code=400, detail="Número de teléfono inválido.")

    # Consultar el operador
    operador = await verificar_operador_async(numero_telefono)

    if operador:
        return {"numero": numero_telefono, "operador": operador}
    else:
        raise HTTPException(status_code=500, detail="No se pudo determinar el operador.")

# Iniciar el servidor: uvicorn nombre_del_archivo:app --reload
if __name__ == "__main__":
    uvicorn.run("vernum2:app", host="127.0.0.1", port=8000, reload=True)
