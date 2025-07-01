import os
import glob
import time
from elasticsearch import Elasticsearch, helpers

ES_HOST = "http://elasticsearch:9200"
es = Elasticsearch(ES_HOST)

index_configs = {
    "incidentes_trafico": {
        "path": "/data/output/filtrados",
        "fields": [
            "uuid", "country", "city", "type", "subtype", "street",
            "speed", "confidence", "x", "y", "pubmillis", "pub_date"
        ],
        "id_field": "uuid"
    },
    "incidentes_por_fecha": {
        "path": "/data/output/por_fecha",
        "fields": ["fecha_legible", "total_eventos"],
        "id_field": "fecha_legible"
    },
    "incidentes_por_ciudad": {
        "path": "/data/output/por_ciudad",
        "fields": ["ciudad", "total_eventos"],
        "id_field": "ciudad"
    },
    "incidentes_por_tipo": {
        "path": "/data/output/por_tipo",
        "fields": ["tipo", "total_eventos"],
        "id_field": "tipo"
    }
}

def countdown(seconds):
    print(f"Iniciando en {seconds} segundos...")
    for remaining in range(seconds, 0, -1):
        print(f"\r{remaining} segundos restantes...", end="", flush=True)
        time.sleep(1)
    print("\r¡Iniciando ahora!            ")

def wait_for_files(paths):
    print("Esperando archivos part-m-* o part-r-* para indexar...")
    while not any(
        glob.glob(os.path.join(path, "part-m-*")) or glob.glob(os.path.join(path, "part-r-*"))
        for path in paths
    ):
        print("Archivos no encontrados. Esperando 2 segundos...")
        time.sleep(2)
    print("¡Archivos encontrados! Iniciando indexación...")

def parse_line(line, fields):
    values = line.strip().split(",")  # Ajusta separador según corresponda
    if len(values) != len(fields):
        print(f"Advertencia: línea ignorada por longitud inválida ({len(values)} campos, esperado {len(fields)}): {line.strip()}")
        return None
    doc = dict(zip(fields, values))
    for key in ["speed", "confidence", "x", "y", "pubmillis", "total_eventos"]:
        if key in doc:
            try:
                if key in ["x", "y"]:
                    doc[key] = float(doc[key])
                elif key in ["speed", "confidence", "total_eventos"]:
                    doc[key] = int(float(doc[key]))
                elif key == "pubmillis":
                    doc[key] = int(doc[key])
            except Exception as e:
                print(f"Advertencia: no se pudo convertir campo {key} con valor '{doc[key]}': {e}")
    return doc

def clear_index(index_name):
    if es.indices.exists(index=index_name):
        print(f"Borrando índice completo: {index_name}")
        es.indices.delete(index=index_name)
    print(f"Creando índice: {index_name}")
    es.indices.create(index=index_name)

def index_directory(index_name, dir_path, fields, id_field):
    clear_index(index_name)

    actions = []
    total_indexed = 0
    files = glob.glob(os.path.join(dir_path, "part-m-*")) + glob.glob(os.path.join(dir_path, "part-r-*"))

    if not files:
        print(f"No se encontraron archivos para indexar en {dir_path}")
        return 0

    for file in files:
        print(f"Indexando archivo: {file}")
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                doc = parse_line(line, fields)
                if doc:
                    doc_id = doc.get(id_field)
                    action = {
                        "_index": index_name,
                        "_source": doc,
                    }
                    if doc_id:
                        action["_id"] = doc_id
                    actions.append(action)
                    total_indexed += 1
                    if len(actions) >= 500:
                        helpers.bulk(es, actions, refresh=True)
                        actions = []
    if actions:
        helpers.bulk(es, actions, refresh=True)

    print(f"✅ Indexación para índice '{index_name}' finalizada: {total_indexed} documentos indexados.\n")
    return total_indexed

def wait_for_index_data(index_name):
    print(f"Verificando que el índice '{index_name}' tenga documentos...")
    while True:
        try:
            count = es.count(index=index_name)['count']
            if count > 0:
                print(f"El índice '{index_name}' tiene {count} documentos. Continuando...")
                break
            else:
                print(f"El índice '{index_name}' tiene 0 documentos. Esperando 5 segundos...")
                time.sleep(5)
        except Exception as e:
            print(f"Error al consultar índice '{index_name}': {e}. Reintentando en 5 segundos...")
            time.sleep(5)

if __name__ == "__main__":
    countdown(30)  # Cuenta regresiva antes de empezar

    wait_for_files([cfg["path"] for cfg in index_configs.values()])

    for index_name, cfg in index_configs.items():
        total = index_directory(index_name, cfg["path"], cfg["fields"], cfg["id_field"])
        if total == 0:
            print(f"¡Atención! No se indexó ningún documento para el índice '{index_name}'.")
        wait_for_index_data(index_name)

        print("Esperando 30 segundos antes de procesar el siguiente índice...")
        time.sleep(30)

