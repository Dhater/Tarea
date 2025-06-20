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
        "id_field": "uuid"  # campo para usar como _id en ES y evitar duplicados
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
    values = line.strip().split(",")
    if len(values) != len(fields):
        return None
    doc = dict(zip(fields, values))
    # Convertir valores numéricos si corresponde
    for key in ["speed", "confidence", "x", "y", "pubmillis", "total_eventos"]:
        if key in doc:
            try:
                if key in ["x", "y"]:
                    doc[key] = float(doc[key])
                elif key in ["speed", "confidence", "total_eventos"]:
                    doc[key] = int(float(doc[key]))  # algunos pueden venir como "10.0"
                elif key == "pubmillis":
                    doc[key] = int(doc[key])
            except:
                pass
    return doc

def clear_index_documents(index_name):
    if es.indices.exists(index=index_name):
        print(f"Borrando documentos en índice: {index_name}")
        # delete_by_query con query match_all borra todos los documentos, no el índice
        es.delete_by_query(index=index_name, body={"query": {"match_all": {}}}, wait_for_completion=True)
    else:
        print(f"Índice {index_name} no existe, se creará.")
        es.indices.create(index=index_name)

def index_directory(index_name, dir_path, fields, id_field):
    clear_index_documents(index_name)

    actions = []
    total_indexed = 0
    files = glob.glob(os.path.join(dir_path, "part-m-*")) + glob.glob(os.path.join(dir_path, "part-r-*"))

    for file in files:
        print(f"Indexando archivo: {file}")
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                doc = parse_line(line, fields)
                if doc:
                    # Usa id_field como _id para evitar duplicados
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
                        helpers.bulk(es, actions)
                        actions = []
    if actions:
        helpers.bulk(es, actions)
    print(f"✅ Indexación para índice '{index_name}' finalizada: {total_indexed} documentos indexados.\n")

if __name__ == "__main__":
    wait_for_files([cfg["path"] for cfg in index_configs.values()])

    for index_name, cfg in index_configs.items():
        index_directory(index_name, cfg["path"], cfg["fields"], cfg["id_field"])
