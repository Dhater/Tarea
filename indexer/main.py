import os
import glob
from elasticsearch import Elasticsearch, helpers

ES_HOST = "http://elasticsearch:9200"
INDEX_NAME = "incidentes_trafico"
DATA_DIR = "/data/output/filtrados"  # dentro del contenedor, porque el volumen se monta ahí

FIELDS = [
    "uuid", "country", "city", "type", "subtype", "street",
    "speed", "confidence", "x", "y", "pubmillis", "pub_date"
]

es = Elasticsearch(ES_HOST)

def parse_line(line):
    values = line.strip().split("\t")
    if len(values) != len(FIELDS):
        return None
    doc = dict(zip(FIELDS, values))
    try:
        doc["speed"] = float(doc["speed"])
        doc["confidence"] = float(doc["confidence"])
        doc["x"] = float(doc["x"])
        doc["y"] = float(doc["y"])
        doc["pubmillis"] = int(doc["pubmillis"])
    except:
        pass
    return doc

def load_files_to_es():
    actions = []
    files = glob.glob(os.path.join(DATA_DIR, "*"))
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                doc = parse_line(line)
                if doc:
                    actions.append({
                        "_index": INDEX_NAME,
                        "_source": doc
                    })
                    if len(actions) >= 500:
                        helpers.bulk(es, actions)
                        actions = []
    if actions:
        helpers.bulk(es, actions)

if __name__ == "__main__":
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME)
    load_files_to_es()
    print("Indexación finalizada")
