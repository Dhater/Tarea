import psycopg2
import redis
import os
import random
import time

# Conexión a PostgreSQL
def connect_postgres():
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'mi_basededatos'),
            user=os.getenv('POSTGRES_USER', 'user'),
            password=os.getenv('POSTGRES_PASSWORD', 'user')
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Error al conectar a PostgreSQL: {e}")
        return None

# Conexión a Redis
def connect_redis():
    try:
        r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)
        return r
    except Exception as e:
        print(f"[ERROR] Error al conectar a Redis: {e}")
        return None

# Limpiar el caché de Redis
def clear_cache():
    redis_client = connect_redis()
    if redis_client:
        try:
            redis_client.flushdb()
            for _ in range(10):
                if redis_client.dbsize() == 0:
                    print("[CACHE] Caché de Redis limpiado exitosamente.")
                    break
                time.sleep(0.5)
            else:
                print("[ERROR] El caché no se vació completamente.")
        except Exception as e:
            print(f"[ERROR] Error al limpiar el caché de Redis: {e}")
    else:
        print("[ERROR] No se pudo conectar a Redis para limpiar el caché.")

# Función principal
def generate_traffic():
    clear_cache()
    total_requests = 10000
    hits = 0

    for request in range(total_requests):
        try:
            random_id = random.randint(1, 10000)
            print(f"[TRAFFIC] Generando tráfico con id: {random_id}, [Request] {request}")

            redis_client = connect_redis()
            if not redis_client:
                print("[ERROR] Error en la conexión a Redis.")
                time.sleep(2)
                continue

            cache_key = f"eventos:{random_id}"
            cached_data = redis_client.get(cache_key)

            if cached_data:
                hits += 1
                print(f"[TRAFFIC] Cache hit para id {random_id}")
            else:
                print(f"[TRAFFIC] Cache miss para id {random_id}")
                postgres_conn = connect_postgres()
                if not postgres_conn:
                    print("[ERROR] Error en la conexión a PostgreSQL.")
                    time.sleep(2)
                    continue

                try:
                    cursor = postgres_conn.cursor()
                    cursor.execute("SELECT id, type, subtype FROM eventos WHERE id = %s", (random_id,))
                    result = cursor.fetchone()
                    cursor.close()

                    if result:
                        event_type = result[1]
                        description = result[2]
                        print(f"[TRAFFIC] Evento encontrado: ID {result[0]}, Tipo: {event_type}, Descripción: {description}")
                        redis_client.setex(cache_key, 3600, str(result))
                        print(f"[TRAFFIC] Datos guardados en Redis para id {random_id}")
                    else:
                        print(f"[TRAFFIC] No se encontraron resultados para id {random_id}")
                except Exception as e:
                    print(f"[ERROR] Error al consultar PostgreSQL: {e}")
                finally:
                    postgres_conn.close()

        except Exception as e:
            print(f"[ERROR] Error al generar tráfico: {e}")

        # Puedes descomentar esta línea si necesitas reducir carga
        # time.sleep(0.001)

    hit_percent = (hits / total_requests) * 100
    print(f"[RESULTADO] Se han registrado {hits} hits de caché.")
    print(f"[RESULTADO] Porcentaje de aciertos: {hit_percent:.2f}%")

    print("[ESPERA] Finalizado. Esperando indefinidamente para análisis externo.")
    while True:
        time.sleep(60)

# Punto de entrada
if __name__ == '__main__':
    generate_traffic()
