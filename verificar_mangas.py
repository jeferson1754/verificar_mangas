from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re


def configurar_navegador():
    """ Configura y devuelve una instancia de WebDriver con opciones optimizadas. """
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")  # Modo sin interfaz gráfica
    chrome_options.add_argument(
        "--ignore-certificate-errors")  # Ignorar errores SSL
    # Evitar problemas en entornos sin GPU
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "--window-size=800,600")  # Tamaño fijo de ventana

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def extraer_enlaces(archivo_entrada):
    """ Lee un archivo y extrae enlaces de manga mediante regex. """
    with open(archivo_entrada, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    patron_enlace = r"Enlace de Verificación:\s*(https?://[^\s]+)"
    return [re.search(patron_enlace, linea).group(1).strip() for linea in lineas if re.search(patron_enlace, linea)]


def forzar_checkbox(driver):
    """ Busca el checkbox y le fuerza el atributo 'checked' si no lo tiene. """
    try:
        # Esperar hasta que el checkbox esté presente en el DOM
        checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "checkbox"))
        )

        # Verificar si está marcado, si no, forzar 'checked'
        if not checkbox.get_attribute("checked"):
            driver.execute_script(
                "arguments[0].setAttribute('checked', 'true');", checkbox)
            print("✔ Checkbox marcado forzadamente.")

    except Exception as e:
        print(f"⚠ Error al forzar el checkbox: {e}")


def presionar_boton_guardar(driver):
    """ Espera y hace clic en el botón 'Guardar' si está presente. """
    try:
        boton_guardar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "verif"))
        )
        boton_guardar.click()
        print("✔ Botón 'Guardar' presionado.")
    except Exception as e:
        print(f"⚠ Error al presionar el botón 'Guardar': {e}")


def obtener_fechas(driver, url):
    """ Abre la URL, marca el checkbox y presiona el botón. Luego extrae las fechas. """
    try:
        driver.get(url)
        forzar_checkbox(driver)
        presionar_boton_guardar(driver)

        # Esperar hasta que las fechas sean visibles y extraerlas
        fechas_elementos = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, "td.fecha"))
        )
        return [fecha.text for fecha in fechas_elementos]
    except Exception as e:
        print(f"⚠ Error al obtener fechas de {url}: {e}")
        return []


def abrir_enlaces_manga(archivo_entrada="resultados.txt"):
    """ Abre los enlaces del archivo, extrae fechas y muestra resultados. """
    driver = configurar_navegador()
    enlaces = extraer_enlaces(archivo_entrada)

    if not enlaces:
        print("⚠ No se encontraron enlaces de manga válidos en el archivo.")
        return

    for enlace in enlaces:
        print(f"🔗 Abriendo: {enlace}")
        fechas = obtener_fechas(driver, enlace)
        print(
            f"📌 **Fechas extraídas:** {fechas if fechas else 'No se encontraron fechas'}")

    driver.quit()


if __name__ == "__main__":
    
    url = "http://localhost/Manga/?sin-fechas="
    obtener_enlaces_principales(url)
    abrir_enlaces_manga()
