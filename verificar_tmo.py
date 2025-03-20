import requests
import time
from plyer import notification

URL = "https://zonatmo.com/items_pending/pending"  # Cambia esto por la URL a monitorear
CHECK_INTERVAL = 120  # 2 minutos
NOTIFY_INTERVAL = 3600  # 1 hora

last_notification_time = 0  # Guarda el tiempo de la última notificación de fallo
attempt_count = 0  # Variable para contar los intentos

def check_website():
    try:
        response = requests.get(URL, timeout=10)
        if response.status_code == 200:
            notification.notify(
                title="Acceso Disponible",
                message=f"La página {URL} está disponible.",
                timeout=10
            )
            return True
    except requests.RequestException:
        pass
    return False

while True:
    attempt_count += 1  # Incrementa el número de intento
    print(f"Intento #{attempt_count} para acceder a {URL}...")  # Muestra el intento y el número
    if check_website():
        last_notification_time = 0  # Reinicia el contador si se puede acceder
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
