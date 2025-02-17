from datetime import datetime

# Arreglos de fechas
arreglo_1 = ['2025-02-02', '2025-02-03', '2025-01-08', '2024-12-30', '2024-12-30',
             '2024-12-03', '2024-12-02', '2024-11-24', '2024-11-03', '2024-09-29']
arreglo_2 = ['2025-01-08 19:53:06', '2024-12-03 17:47:01', '2024-12-02 17:38:09', '2024-11-24 18:35:05', '2024-11-03 19:05:55',
             '2024-09-29 21:47:35', '2024-09-04 20:21:17', '2024-08-26 20:54:24', '2024-08-17 13:25:42', '2024-08-09 22:09:51']


def comparar_fechas(arreglo_1, arreglo_2):

    fechas_1 = list(dict.fromkeys(arreglo_1))

    # Convertir las fechas del arreglo 2 a formato 'YYYY-MM-DD' (quitando la hora)
    arreglo_2_convertido = {datetime.strptime(
        fecha, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") for fecha in arreglo_2}

    fechas_2 = list(dict.fromkeys(arreglo_2_convertido))

    # Lista para guardar fechas incorrectas
    fechas_incorrectas = [fecha for fecha in fechas_1 if fecha not in fechas_2]

    # Verificar si todas las fechas coinciden
    if not fechas_incorrectas:
        print("✅ Todas las fechas coinciden. Ejecutando acción...")
        # Aquí puedes poner la acción que quieres ejecutar
    else:
        print("❌ No todas las fechas coinciden.")
        for fecha in fechas_incorrectas:
            print(f"⚠️ La fecha {fecha} no está en el arreglo 2.")
