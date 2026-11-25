import csv
import os
from datetime import datetime, timedelta, timezone
import tinytuya

API_KEY = os.environ["TUYA_API_KEY"]
API_SECRET = os.environ["TUYA_API_SECRET"]
DEVICE_ID = os.environ["TUYA_DEVICE_ID"]
REGION = "us"
ARCHIVO_CSV = "datos_estacion.csv"

cloud = tinytuya.Cloud(
    apiRegion=REGION,
    apiKey=API_KEY,
    apiSecret=API_SECRET,
    apiDeviceID=DEVICE_ID,
)

COLUMNAS = [
    "fecha_hora",
    "temp_interior_C",
    "humedad_interior_%",
    "temp_exterior_C",
    "humedad_exterior_%",
    "presion_mmHg",
    "viento_prom_m/s",
    "viento_rafaga_m/s",
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


if not os.path.exists(ARCHIVO_CSV):
    with open(ARCHIVO_CSV, mode="w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerow(COLUMNAS)

respuesta = cloud.getstatus(DEVICE_ID)
if not respuesta.get("success"):
    raise RuntimeError(f"Error de API Tuya: {respuesta}")

sensores = {item["code"]: item["value"] for item in respuesta.get("result", [])}
hora_ecuador = datetime.now(timezone(timedelta(hours=-5))).strftime("%Y-%m-%d %H:%M:%S")

fila = [
    hora_ecuador,
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

print(f"[{hora_ecuador}] Fila agregada correctamente.")