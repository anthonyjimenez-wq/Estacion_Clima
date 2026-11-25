import csv
import os
import time
from datetime import datetime
import tinytuya

DEVICE_ID = "eb322c9cdb943bba14yguj"
ARCHIVO_CSV = "datos_estacion.csv"
INTERVALO_SEGUNDOS = 60  # Cambia a 300 para guardar cada 5 minutos

cloud = tinytuya.Cloud()

COLUMNAS = [
    "fecha_hora",
    "temp_interior_C",
    "humedad_interior_%",
    "temp_exterior_C",
    "humedad_exterior_%",
    "presion",
    "viento_prom_mps",
    "viento_rafaga_mps",
    "lluvia_1h_mm",
    "lluvia_24h_mm",
    "lluvia_tasa_mm",
    "indice_uv",
    "punto_rocio_C",
    "sensacion_termica_C",
    "indice_calor_C",
    "sensacion_viento_C",
]


def escalar(sensores, clave, divisor=1, valor_nulo=None):
    val = sensores.get(clave)
    if val is None or val == valor_nulo:
        return ""
    return round(val / divisor, 2) if divisor != 1 else val


# Crea el archivo con encabezados si aún no existe
if not os.path.exists(ARCHIVO_CSV):
    with open(ARCHIVO_CSV, mode="w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerow(COLUMNAS)

print(f"Iniciando registro cada {INTERVALO_SEGUNDOS} segundos en '{ARCHIVO_CSV}'...")
print("Presiona Ctrl + C en la terminal para detener.\n")

while True:
    try:
        respuesta = cloud.getstatus(DEVICE_ID)
        if respuesta.get("success"):
            sensores = {item["code"]: item["value"] for item in respuesta.get("result", [])}
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            fila = [
                ahora,
                escalar(sensores, "temp_current", 10),
                escalar(sensores, "humidity_value"),
                escalar(sensores, "temp_current_external", 10),
                escalar(sensores, "humidity_outdoor"),
                escalar(sensores, "atmospheric_pressture"),
                escalar(sensores, "windspeed_avg", 10),
                escalar(sensores, "windspeed_gust", 10),
                escalar(sensores, "rain_1h", 10),
                escalar(sensores, "rain_24h", 10),
                escalar(sensores, "rain_rate", 10),
                escalar(sensores, "uv_index"),
                escalar(sensores, "dew_point_temp", 10),
                escalar(sensores, "feellike_temp", 10),
                escalar(sensores, "heat_index", 10),
                escalar(sensores, "windchill_index", 10, valor_nulo=-400),
            ]

            with open(ARCHIVO_CSV, mode="a", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerow(fila)

            print(f"[{ahora}] Guardado -> Ext: {fila[3]}°C | Hum: {fila[4]}% | Pres: {fila[5]} | Viento: {fila[6]} m/s")
        else:
            print(f"Error de API Tuya: {respuesta}")

    except KeyboardInterrupt:
        print("\nRegistro detenido por el usuario.")
        break
    except Exception as e:
        print(f"Error de conexión (se reintentará): {e}")

    time.sleep(INTERVALO_SEGUNDOS)