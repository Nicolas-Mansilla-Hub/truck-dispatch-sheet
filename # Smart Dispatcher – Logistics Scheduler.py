# Smart Dispatcher – Logistics Scheduler and Tracker
# Simulación de tareas clave para un Truck Traffic Coordinator

import pandas as pd
import time
from datetime import datetime, timedelta
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from geopy.distance import geodesic
import smtplib
from email.mime.text import MIMEText

# ---------------------------- CONFIGURACIÓN ----------------------------
# Credenciales de Google Sheets (usar tu propio JSON de API)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
client = gspread.authorize(creds)

# Conectar a la hoja de cálculo
sheet = client.open("Truck Dispatch Sheet").sheet1

# ---------------------------- FUNCIONES PRINCIPALES ----------------------------

# Cargar rutas desde Google Sheets
def cargar_rutas():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Simular ubicación GPS (lat, lon) con leve desviación
def simular_gps(lat, lon):
    return (lat + random.uniform(-0.01, 0.01), lon + random.uniform(-0.01, 0.01))

# Calcular ETA (tiempo estimado de llegada) basado en velocidad promedio (km/h)
def calcular_eta(origen, destino, velocidad_kmh=50):
    distancia_km = geodesic(origen, destino).km
    eta_horas = distancia_km / velocidad_kmh
    return timedelta(hours=eta_horas)

# Enviar alerta por email (ejemplo básico con SMTP Gmail)
def enviar_alerta(destinatario, asunto, mensaje):
    remitente = "nicomansilla.777@gmail.com"
    password = "pmpdlwwqsucupate"
    msg = MIMEText(mensaje)
    msg['Subject'] = asunto
    msg['From'] = remitente
    msg['To'] = destinatario

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())

# Procesar rutas y detectar demoras

def procesar_rutas(df):
    ahora = datetime.now()
    for idx, row in df.iterrows():
        origen = (row['origin_lat'], row['origin_lon'])
        destino = (row['dest_lat'], row['dest_lon'])
        eta = calcular_eta(origen, destino)
        llegada_estimada = row['dispatch_time'] + eta

        # Simulación de retraso
        simulacion_llegada = llegada_estimada + timedelta(minutes=random.choice([0, 10, 20, 30]))

        if simulacion_llegada > llegada_estimada + timedelta(minutes=15):
            enviar_alerta(
                row['customer_email'],
                "[Alerta] Posible demora en la entrega",
                f"Hola {row['customer_name']}, detectamos una posible demora en tu entrega programada. Nueva ETA: {simulacion_llegada.strftime('%H:%M')}"
            )

# ---------------------------- EJECUCIÓN ----------------------------

if __name__ == "__main__":
    rutas = cargar_rutas()
    rutas['dispatch_time'] = pd.to_datetime(rutas['dispatch_time'])
    procesar_rutas(rutas)
    
    
rutas = cargar_rutas()
print(rutas) 
print("✅ Conexión exitosa con Google Sheets")