import requests
import json
import time
import os
import csv
import psycopg2
from datetime import datetime
import matplotlib as plt

#Scraper
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

TARGET_COUNT = 20000
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

#Inicio Scraper
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


def exportar_eventos_a_csv():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=5432
    )
    cur = conn.cursor()
    
    # Incluye pubMillis en la consulta
    cur.execute("""
        SELECT uuid, country, city, type, subtype, street, speed,
               confidence, x, y, pubMillis
        FROM eventos
    """)

    ruta_salida = "/csv/eventos.csv"
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    with open(ruta_salida, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Agrega encabezado con pub_date
        headers = [desc[0] for desc in cur.description]
        headers.append("pub_date")
        writer.writerow(headers)

        for row in cur.fetchall():
            *resto, pubMillis = row
            # Solo fecha YYYY-MM-DD, sin hora
            pub_date = datetime.fromtimestamp(pubMillis / 1000).strftime("%Y-%m-%d")
            writer.writerow(resto + [pubMillis, pub_date])

    print(f"✅ Exportado a {ruta_salida}")
    cur.close()
    conn.close()

#Graficador
def analizar_y_graficar_archivo(archivo, titulo, nombre_salida, tipo_grafico="barra"):
    claves = []
    valores = []

    with open(archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            partes = linea.strip().split('\t')
            if len(partes) == 2:
                clave, valor = partes
                claves.append(clave)
                valores.append(int(valor))

    plt.figure(figsize=(10, 6))

    if tipo_grafico == "barra":
        # Ordenar fechas si es posible
        try:
            # Intentamos convertir claves a fechas para ordenar
            fechas = [datetime.strptime(c, "%Y-%m-%d") for c in claves]
            pares = sorted(zip(fechas, valores), key=lambda x: x[0])
            fechas_ordenadas = [f.strftime("%Y-%m-%d") for f, v in pares]
            valores_ordenados = [v for f, v in pares]
            claves, valores = fechas_ordenadas, valores_ordenados
        except Exception as e:
            print(f"⚠️ No se pudieron ordenar fechas: {e}")

        plt.bar(claves, valores, color='skyblue')
        plt.xlabel("Fecha")
        plt.ylabel("Cantidad")
        plt.xticks(rotation=45)

    elif tipo_grafico == "torta":
        plt.pie(valores, labels=claves, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Para que el gráfico sea circular

    plt.title(titulo)
    plt.tight_layout()

    ruta_img = f"/output/grafico_{nombre_salida}.png"
    plt.savefig(ruta_img)
    print(f"🖼️ Gráfico guardado en: {ruta_img}")
    plt.close()

#Revisar archivos
def revisar_y_analizar_output_pig():
    ruta_output = "/output"
    archivos_esperados = {
        "filtrados/part-r-00000": ("Eventos filtrados", "filtrados", "torta"),
        "por_ciudad/part-r-00000": ("Eventos por ciudad", "ciudad", "torta"),
        "por_tipo/part-r-00000": ("Eventos por tipo", "tipo", "torta"),
        "por_fecha/part-r-00000": ("Eventos por fecha", "fecha", "barra")
    }
    encontrados = 0

    for archivo_rel, (titulo, nombre_img, tipo_graf) in archivos_esperados.items():
        ruta_archivo = os.path.join(ruta_output, archivo_rel)
        if os.path.exists(ruta_archivo):
            print(f"📂 Archivo encontrado: {ruta_archivo}")
            encontrados += 1
            analizar_y_graficar_archivo(ruta_archivo, titulo, nombre_img, tipo_graf)

    if encontrados == 0:
        print("❗ No se encontraron archivos de salida de Pig.")
#Conteo eventos
def obtener_total_maximo_eventos():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=5432
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM eventos;")
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        print(f"📊 Total máximo de eventos en la base: {total}")
        return total
    except Exception as e:
        print(f"❌ Error al obtener total de eventos: {e}")
        return None
#Insertar
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
exportar_eventos_a_csv()
revisar_y_analizar_output_pig()
# 🔄 Espera infinita mostrando la hora
print("🕒 Esperando indefinidamente. Mostrando hora actual cada 30 segundos...")
try:
    while True:
        print("🕒 Hora actual:", time.strftime("%Y-%m-%d %H:%M:%S"))
        time.sleep(30)
except KeyboardInterrupt:
    print("🛑 Finalizando espera...")

