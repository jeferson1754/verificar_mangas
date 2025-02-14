from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import re


def configurar_navegador():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")  # Modo headless si lo necesitas
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignorar errores SSL
    chrome_options.add_argument("--disable-gpu")  # Evitar problemas en entornos sin GPU
    chrome_options.add_argument("--window-size=800,600")  # Definir tamaño de ventana

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def abrir_enlaces_manga(archivo_entrada="resultados.txt"):
    # Configurar el navegador
    driver = configurar_navegador()

    # Abrir el archivo de texto que contiene los enlaces
    with open(archivo_entrada, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    # Expresión regular para extraer enlaces del manga
    enlace_manga_pattern = r"Enlace de Verificación:\s*(https?://[^\s]+)"

    # Lista para almacenar los enlaces válidos
    enlaces_manga = []

    for linea in lineas:
        # Buscar el enlace usando la expresión regular
        match = re.search(enlace_manga_pattern, linea)
        if match:
            enlace = match.group(1).strip()  # Extraemos el enlace
            enlaces_manga.append(enlace)

    # Si se encontraron enlaces, visitarlos
    if enlaces_manga:
        for enlace in enlaces_manga:
            try:
                print(f"Abriendo el enlace: {enlace}")

                fechas = obtener_fechas(enlace)
                time.sleep(3)  # Esperar 3 segundos para cargar la página
                print("\n📌 **Fechas extraídas:**", fechas)
            except Exception as e:
                print(f"Error al abrir el enlace {enlace}: {e}")
    else:
        print("No se encontraron enlaces de manga válidos en el archivo.")

    # Cerrar el navegador
    driver.quit()


def obtener_fechas(url):

    driver = configurar_navegador()
   # Abre la página

    try:

        # Sustituir por la URL de la página donde se encuentra la tabla
        driver.get(url)
        # Encontrar todos los <td> con la clase "fecha"
        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "td.fecha"))  # Esperamos hasta que las celdas con fecha sean visibles
        )

        # Obtener todas las celdas con la clase "fecha"
        celdas_fecha = driver.find_elements(By.CSS_SELECTOR, "td.fecha")


        # Crear una lista con las fechas extraídas
        fechas = [celda.text.strip() for celda in celdas_fecha]

        # Imprimir las fechas extraídas
        primeras_10_fechas = fechas[:10]  # Toma las primeras 10 fechas

        # Imprimir las últimas 10 fechas extraídas
        print(f"Últimas 10 fechas extraídas: {primeras_10_fechas}")

        return primeras_10_fechas  # Retornar las últimas 10 fechas

    except Exception as e:
        print(f"Error al extraer las fechas:")

    finally:
        driver.quit()


if __name__ == "__main__":
    abrir_enlaces_manga()
