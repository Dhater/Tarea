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
        ]
    },
    "incidentes_por_fecha": {
        "path": "/data/output/por_fecha",
        "fields": ["fecha_legible", "total_eventos"]
    },
    "incidentes_por_ciudad": {
        "path": "/data/output/por_ciudad",
        "fields": ["ciudad", "total_eventos"]
    },
    "incidentes_por_tipo": {
        "path": "/data/output/por_tipo",
        "fields": ["tipo", "total_eventos"]
    }
}

def wait_for_files(paths):
    print("Esperando archivos part-m-* o part-r-* para indexar...")
    while not any(glob.glob(os.path.join(path, "part-m-*")) or glob.glob(os.path.join(path, "part-r-*")) for path in paths):
        print("Archivos no encontrados. Esperando 2 segundos...")
        time.sleep(2)
    print("¡Archivos encontrados! Iniciando indexación...")

def parse_line(line, fields):
    values = line.strip().split(",")
    if len(values) != len(fields):
        return None
    return dict(zip(fields, values))

def index_directory(index_name, dir_path, fields):
    actions = []
    total_indexed = 0
    files = glob.glob(os.path.join(dir_path, "part-m-*")) + glob.glob(os.path.join(dir_path, "part-r-*"))

    for file in files:
        print(f"Indexando archivo: {file}")
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                doc = parse_line(line, fields)
                if doc:
                    actions.append({
                        "_index": index_name,
                        "_source": doc
                    })
                    total_indexed += 1
                    if len(actions) >= 500:
                        helpers.bulk(es, actions)
                        actions = []
    if actions:
        helpers.bulk(es, actions)
    print(f"Indexación para índice '{index_name}' finalizada: {total_indexed} documentos indexados.")

if __name__ == "__main__":
    wait_for_files([cfg["path"] for cfg in index_configs.values()])

    for index_name, cfg in index_configs.items():
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name)
        index_directory(index_name, cfg["path"], cfg["fields"])
