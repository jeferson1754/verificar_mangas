from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import re
from plyer import notification

URL = "https://zonatmo.com/"  # URL que deseas verificar
CHECK_INTERVAL = 120  # 2 minutos
NOTIFY_INTERVAL = 3600  # 1 hora

last_notification_time = 0  # Guarda el tiempo de la última notificación de fallo
attempt_count = 0  # Variable para contar los intentos

def configurar_navegador():
    """ Configura y devuelve una instancia de WebDriver con opciones optimizadas. """
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")  # Modo sin interfaz gráfica
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignorar errores SSL
    chrome_options.add_argument("--disable-gpu")  # Evitar problemas en entornos sin GPU
    chrome_options.add_argument("--window-size=800,600")  # Tamaño fijo de ventana

    service = Service(ChromeDriverManager().install())  # Instalar y configurar el driver automáticamente
    return webdriver.Chrome(service=service, options=chrome_options)

def check_website():
    """ Verifica si la página está accesible. """
    try:
        driver = configurar_navegador()
        driver.get(URL)
        
        # Espera a que la página se cargue (hasta que se cargue el título)
        WebDriverWait(driver, 10).until(lambda d: d.title != '')
        
        # Si la página tiene un título, se considera que la carga fue exitosa
        if driver.title:
            print(f"Acceso exitoso a {URL}.")
            notification.notify(
                title="Acceso Disponible",
                message=f"La página {URL} está disponible.",
                timeout=10
            )
            driver.quit()  # Cerrar el navegador
            return True
        else:
            print(f"Acceso fallido a {URL}.")
            driver.quit()
    except Exception as e:
        print(f"Error al intentar acceder a {URL}: {e}")
        driver.quit()  # Asegurarse de cerrar el navegador si hay un error
    return False

# Bucle para verificar el acceso cada 2 minutos
while True:
    attempt_count += 1  # Incrementa el número de intento
    print(f"Intento #{attempt_count} para acceder a {URL}...")  # Muestra el intento y el número
    if check_website():
        last_notification_time = 0  # Reinicia el contador si se puede acceder
        break 
    else:
        current_time = time.time()
        if last_notification_time == 0 or (current_time - last_notification_time) >= NOTIFY_INTERVAL:
            notification.notify(
                title="Acceso No Disponible",
                message=f"No se pudo acceder a {URL}. Se sigue intentando cada 2 minutos.",
                timeout=10
            )
            last_notification_time = current_time  # Actualiza el tiempo de la última notificación

    time.sleep(CHECK_INTERVAL)
