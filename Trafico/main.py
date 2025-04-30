import psycopg2
import time
import os
import random
import requests
from datetime import datetime
import threading

# Función para establecer la conexión a la base de datos
def connect():
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'mi_basededatos'),
            user=os.getenv('POSTGRES_USER', 'user'),
            password=os.getenv('POSTGRES_PASSWORD', 'user')
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Código del error: {e.__class__.__name__}")
        return None

# Función para obtener lista fija de tablas válidas
def get_tables(_conn=None):
    # Siempre devolver 'eventos', ya que ahora no es necesario elegir aleatoriamente
    return ['eventos']

# Función para generar tráfico
def generate_traffic():
    a = False
    if a:  # Si a es True, se ejecuta el bloque
        while True:
            try:
                print(f"[TRAFFIC] Generando tráfico a las {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                # Obtener lista de tablas válidas
                conn = connect()
                if conn is None:
                    print(f"[ERROR] Código del error: DatabaseConnectionError")
                    time.sleep(5)
                    continue

                tables = get_tables(conn)
                # Cerrar la conexión
                conn = None

                if not tables:
                    print(f"[TRAFFIC] No hay tablas válidas definidas.")
                    time.sleep(2)
                    continue

                # Siempre usar la tabla 'eventos'
                table = 'eventos'
                random_id = random.randint(1, 10000)

                # Solo enviar el id
                query = {"id": random_id}

                # Imprimir el ID que se va a enviar
                print(f"[TRAFFIC] Enviando consulta con ID: {query['id']}")

                # Enviar consulta al servicio de caché
                response = requests.post(
                    os.getenv('CACHE_SERVICE_URL', 'http://localhost:5000/query'),
                    json=query,
                    timeout=3
                )

                # Solo imprimir el código del error si hay uno
                if response.status_code != 200:
                    print(f"[ERROR] Código del error HTTP: {response.status_code}")

            except Exception as e:
                print(f"[ERROR] Código del error: {e.__class__.__name__}")

            time.sleep(10)

# Ejecutar reloj en hilo paralelo
def print_time_every_10_seconds():
    while True:
        print(f"[INFO] Hora actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(30)

# Ejecutar tráfico
thread = threading.Thread(target=print_time_every_10_seconds)
thread.daemon = True
thread.start()

# Ejecutar tráfico
generate_traffic()
