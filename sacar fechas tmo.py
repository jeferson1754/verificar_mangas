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
    # Ejecuta sin mostrar la ventana del navegador
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=800,600")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def abrir_enlaces_manga(archivo_entrada="resultados.txt"):
    # Configurar el navegador
    driver = configurar_navegador()

    # Abrir el archivo de texto que contiene los enlaces
    with open(archivo_entrada, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    # Expresión regular para extraer enlaces del manga
    enlace_manga_pattern = r"Enlace del Manga:\s*(https?://[^\s]+)"

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

                fechas = interactuar_con_capitulo(enlace)
                time.sleep(3)  # Esperar 3 segundos para cargar la página
                print("\n📌 **Fechas extraídas:**", fechas)
            except Exception as e:
                print(f"Error al abrir el enlace {enlace}: {e}")
    else:
        print("No se encontraron enlaces de manga válidos en el archivo.")

    # Cerrar el navegador
    driver.quit()


def interactuar_con_capitulo(url):

    driver = configurar_navegador()
   # Abre la página
    driver.get(url)

    try:
        # Esperar a que los botones "btn-collapse" sean visibles
        botones = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "btn-collapse"))
        )

        fechas = []

        for boton in botones[:10]:  # Tomar solo los primeros 10 botones
            try:
                # Extraemos el atributo 'onclick'
                onclick_value = boton.get_attribute("onclick")
                match = re.search(r"collapseChapter\('(.+?)'\)", onclick_value)

                if match:
                    div_id = match.group(1)  # Extraemos el id del div
                    #print(f"ID del div: {div_id}")

                    # Haz clic en el enlace
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", boton)

                    #print("✅ Enlace clickeado.")

                    # Esperar un momento para ver si se expande automáticamente
                    time.sleep(2)

                    # **Verificar si el div se hizo visible**
                    div = driver.find_element(By.ID, div_id)

                    if not div.is_displayed():
                        #print("⚠️ El div sigue oculto. Intentando forzar visibilidad con JS...")
                        driver.execute_script(
                            "arguments[0].style.display = 'block';", div)

                    # Verificar nuevamente si es visible
                    if div.is_displayed():
                        #print(f"📌 Contenido del div con id {div_id}:")
                        try:
                            date_span = div.find_element(
                                By.CSS_SELECTOR, "span.badge.badge-primary.p-2")
                            fecha = date_span.text
                            fechas.append(fecha)
                            print(f"📅 Fecha encontrada: {fecha}")
                        except:
                            print("❌ No se encontró la fecha en el div.")
                    else:
                        print("❌ No se pudo hacer visible el div.")

                else:
                    print("❌ No se pudo extraer el ID del div.")

            except Exception as e:
                print(f"🚨 Error con un botón: {e}")

        return fechas

    except Exception as e:
        print(f"🚨 Error durante la interacción: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    abrir_enlaces_manga()
