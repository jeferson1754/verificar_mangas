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


def obtener_enlaces_principales(url, archivo_salida="resultados.txt"):
    driver = configurar_navegador()
    driver.get(url)

    # Esperar a que cargue la página
    time.sleep(3)

    # Obtener todos los enlaces con clase "link" (manga)
    enlaces_manga = driver.find_elements(By.CSS_SELECTOR, "a.link")

    # Obtener todos los enlaces con clase "chart" (verificación)
    enlaces_verificacion = driver.find_elements(By.CSS_SELECTOR, "a.chart")

    # Validar que existan enlaces
    if not enlaces_manga:
        print("No se encontraron enlaces de manga.")
    if not enlaces_verificacion:
        print("No se encontraron enlaces de verificación.")

    # Abrir archivo para escribir los resultados
    with open(archivo_salida, "w", encoding="utf-8") as archivo:
        # Recorrer los enlaces con un while
        index = 0
        while index < max(len(enlaces_manga), len(enlaces_verificacion)):
            manga = enlaces_manga[index].get_attribute(
                "href") if index < len(enlaces_manga) else "No disponible"
            verificacion = enlaces_verificacion[index].get_attribute(
                "href") if index < len(enlaces_verificacion) else "No disponible"

            # Escribir los resultados en el archivo
            archivo.write(f"[{index + 1}] Enlace del Manga: {manga}\n")
            archivo.write(
                f"[{index + 1}] Enlace de Verificación: {verificacion}\n")
            archivo.write("-" * 50 + "\n")

            index += 1

    print(f"Los resultados se han guardado en {archivo_salida}.")
    driver.quit()


def extraer_enlaces(archivo_entrada):
    """ Lee un archivo y extrae enlaces mediante regex. """
    with open(archivo_entrada, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    patron_verificacion = r"Enlace de Verificación:\s*(https?://[^\s]+)"
    patron_manga = r"Enlace del Manga:\s*(https?://[^\s]+)"

    enlaces_verificacion = [re.search(patron_verificacion, linea).group(
        1).strip() for linea in lineas if re.search(patron_verificacion, linea)]
    enlaces_manga = [re.search(patron_manga, linea).group(
        1).strip() for linea in lineas if re.search(patron_manga, linea)]

    return enlaces_verificacion, enlaces_manga


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


def obtener_fechas_tmo(driver, url):

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
                    # print(f"ID del div: {div_id}")

                    # Haz clic en el enlace
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", boton)

                    # print("✅ Enlace clickeado.")

                    # Esperar un momento para ver si se expande automáticamente
                    time.sleep(2)

                    # **Verificar si el div se hizo visible**
                    div = driver.find_element(By.ID, div_id)

                    if not div.is_displayed():
                        # print("⚠️ El div sigue oculto. Intentando forzar visibilidad con JS...")
                        driver.execute_script(
                            "arguments[0].style.display = 'block';", div)

                    # Verificar nuevamente si es visible
                    if div.is_displayed():
                        # print(f"📌 Contenido del div con id {div_id}:")
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



def obtener_fechas_verif(driver, url):

    driver.get(url)

    try:

        # Encontrar todos los <td> con la clase "fecha"
        WebDriverWait(driver, 10).until(
            # Esperamos hasta que las celdas con fecha sean visibles
            EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, "td.fecha"))
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



def obtener_fechas(driver, url):
    """ Abre la URL, marca el checkbox y presiona el botón. Luego extrae las fechas. """
    try:
        driver.get(url)
        forzar_checkbox(driver)
        presionar_boton_guardar(driver)

    except Exception as e:
        print(f"⚠ Error al obtener fechas de {url}: {e}")
        return []


def comparar_fechas(arreglo_1, arreglo_2, driver, enlace):
    """ Compara las fechas de los arreglos y obtiene las fechas correctas si coinciden. """
    # Convertir las fechas del arreglo 2 a formato 'YYYY-MM-DD' (quitando la hora)
    fechas_1 = list(dict.fromkeys(arreglo_1))
    fechas_2 = {datetime.strptime(
        fecha, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") for fecha in arreglo_2}

    # Verificar si todas las fechas coinciden
    fechas_incorrectas = [fecha for fecha in fechas_1 if fecha not in fechas_2]

    if not fechas_incorrectas:
        print("✅ Todas las fechas coinciden. Ejecutando acción...")
        fechas = obtener_fechas(driver, enlace)
        print(
            f"📌 **Fechas extraídas:** {fechas if fechas else 'No se encontraron fechas'}")
        return True  # Fechas correctas
    else:
        print("❌ No todas las fechas coinciden.")
        for fecha in fechas_incorrectas:
            print(f"⚠️ La fecha {fecha} no está en el arreglo 2.")
        return False  # Fechas incorrectas


def abrir_enlaces_manga(archivo_entrada="resultados.txt"):
    """ Abre los enlaces del archivo, extrae fechas y muestra resultados. """
    driver = configurar_navegador()
    enlaces_verificacion, enlaces_manga = extraer_enlaces(archivo_entrada)

    if not (enlaces_manga and enlaces_verificacion):
        print("⚠ No se encontraron enlaces válidos de manga o verificación.")
        return

    # Contadores de mangas correctos e incorrectos
    mangas_correctos = 0
    mangas_erroneos = 0

    # Aseguramos que ambos bucles iteren de manera sincronizada
    for enlace_manga, enlace_verif in zip(enlaces_manga, enlaces_verificacion):
        print(f"🔗 Abriendo manga: {enlace_manga}")
        fechas_tmo = obtener_fechas_tmo(driver, enlace_manga)

        print(f"🔗 Abriendo verificación: {enlace_verif}")
        fechas_verif = obtener_fechas_verif(driver, enlace_verif)

        # Comparar las fechas para el par actual
        if comparar_fechas(fechas_tmo, fechas_verif, driver, enlace_verif):
            mangas_correctos += 1
        else:
            mangas_erroneos += 1

    # Al finalizar todos los ciclos, mostrar los totales
    print(f"\n✅ Total de mangas correctos: {mangas_correctos}")
    print(f"❌ Total de mangas con errores: {mangas_erroneos}")

    driver.quit()


if __name__ == "__main__":
    #url = "https://inventarioncc.infinityfreeapp.com/Manga/?sin-fechas="
    url = "https://inventarioncc.infinityfreeapp.com/Manga/Pendientes/?sin-fechas="
    obtener_enlaces_principales(url)
    abrir_enlaces_manga()
