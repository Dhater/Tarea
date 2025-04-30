import requests
import json
import time
import os

def fetch_waze_events(lat_min, lat_max, lng_min, lng_max):
    url = (
        f"https://www.waze.com/live-map/api/georss?"
        f"top={lat_max}&bottom={lat_min}&left={lng_min}&right={lng_max}"
        f"&env=row&types=alerts,traffic"
    )
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('alerts', []), data.get('traffic', [])
    except Exception as e:
        print("❌ Error al obtener datos:", e)
        return [], []

# Parámetros
lat_min = -33.418863153828454
lat_max = -33.37380423388275
lng_min = -70.73255538940431
lng_max = -70.54201126098634

TARGET_COUNT = 10000
unique_events = {}

# Ruta del archivo
ruta_archivo = os.path.join(os.getcwd(), "eventos_waze.json")
if os.path.exists(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        try:
            existing_events = json.load(f)
            unique_events = {event['id']: event for event in existing_events}
            print(f"♻️ Se cargaron {len(unique_events)} eventos previos.")
        except json.JSONDecodeError:
            print("⚠️ El archivo existente está corrupto. Se creará uno nuevo.")

print("🚀 Iniciando scraping...")

while len(unique_events) < TARGET_COUNT:
    alerts, traffic = fetch_waze_events(lat_min, lat_max, lng_min, lng_max)
    new_events_in_batch = 0

    for event in alerts + traffic:
        if 'id' in event and event['id'] not in unique_events:
            unique_events[event['id']] = event
            new_events_in_batch += 1

    print(f"📊 Total: {len(unique_events)}/{TARGET_COUNT} | Nuevos en este ciclo: {new_events_in_batch}")

    # Guardar si hubo al menos un evento nuevo
    if new_events_in_batch > 0:
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(list(unique_events.values()), f, ensure_ascii=False, indent=2)
            print(f"💾 Archivo actualizado: {ruta_archivo} (Eventos guardados: {len(unique_events)})")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")

    time.sleep(10)

# Guardar los eventos restantes al finalizar
with open(ruta_archivo, 'w', encoding='utf-8') as f:
    json.dump(list(unique_events.values()), f, ensure_ascii=False, indent=2)
print(f"✅ ¡Scraping completado! Archivo final: {ruta_archivo}")

import psycopg2

def insertar_eventos_en_postgres(eventos):
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=5432
    )
    cur = conn.cursor()

    # Crear tablas si no existen
    cur.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id SERIAL PRIMARY KEY,
        uuid VARCHAR(50) UNIQUE,
        country VARCHAR(5),
        city VARCHAR(100),
        type VARCHAR(50),
        subtype VARCHAR(50),
        street VARCHAR(200),
        speed INTEGER,
        confidence INTEGER,
        reliability INTEGER,
        reportRating INTEGER,
        roadType INTEGER,
        magvar INTEGER,
        x FLOAT,
        y FLOAT,
        reportBy VARCHAR(100),
        pubMillis BIGINT,
        reportMood INTEGER
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS comentarios (
        id SERIAL PRIMARY KEY,
        evento_uuid VARCHAR(50) REFERENCES eventos(uuid),
        reportMillis BIGINT,
        isThumbsUp BOOLEAN,
        text TEXT
    );
    """)

    # Insertar eventos
    for evento in eventos:
        try:
            cur.execute("""
                INSERT INTO eventos (uuid, country, city, type, subtype, street, speed, confidence, reliability, reportRating, roadType, magvar, x, y, reportBy, pubMillis, reportMood)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (uuid) DO NOTHING
            """, (
                evento.get('uuid'),
                evento.get('country'),
                evento.get('city'),
                evento.get('type'),
                evento.get('subtype'),
                evento.get('street'),
                evento.get('speed'),
                evento.get('confidence'),
                evento.get('reliability'),
                evento.get('reportRating'),
                evento.get('roadType'),
                evento.get('magvar'),
                evento.get('location', {}).get('x'),
                evento.get('location', {}).get('y'),
                evento.get('reportBy'),
                evento.get('pubMillis'),
                evento.get('reportMood')
            ))

            for comentario in evento.get('comments', []):
                cur.execute("""
                    INSERT INTO comentarios (evento_uuid, reportMillis, isThumbsUp, text)
                    VALUES (%s, %s, %s, %s)
                """, (
                    evento.get('uuid'),
                    comentario.get('reportMillis'),
                    comentario.get('isThumbsUp'),
                    comentario.get('text')
                ))

        except Exception as e:
            print(f"❌ Error al insertar evento {evento.get('id')}: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Insertados {len(eventos)} eventos en PostgreSQL.")

# ---------
# Llamar a la función de inserción después de terminar el scraping
try:
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        eventos = json.load(f)
        insertar_eventos_en_postgres(eventos)
except Exception as e:
    print(f"❌ Error al insertar en base de datos: {e}")

# 🔄 Espera infinita mostrando la hora
print("🕒 Esperando indefinidamente. Mostrando hora actual cada 30 segundos...")
try:
    while True:
        print("🕒 Hora actual:", time.strftime("%Y-%m-%d %H:%M:%S"))
        time.sleep(30)
except KeyboardInterrupt:
    print("🛑 Finalizando espera...")

