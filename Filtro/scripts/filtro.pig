-- Cargar desde HDFS (usa ruta relativa dentro de HDFS)
raw = LOAD '/pig/input/eventos.csv' USING PigStorage(',')
       AS (uuid:chararray, country:chararray, city:chararray,
           type:chararray, subtype:chararray, street:chararray,
           speed:int, confidence:int, x:float, y:float, pubMillis:long);

-- Filtrar campos no vacíos
limpios = FILTER raw BY 
  (uuid IS NOT NULL AND uuid != '') AND
  (country IS NOT NULL AND country != '') AND
  (city IS NOT NULL AND city != '') AND
  (type IS NOT NULL AND type != '') AND
  (subtype IS NOT NULL AND subtype != '') AND
  (street IS NOT NULL AND street != '') AND
  (x IS NOT NULL) AND (y IS NOT NULL) AND (pubMillis IS NOT NULL);

-- Guardar resultados en HDFS
STORE limpios INTO '/pig/output/filtrados' USING PigStorage(',');
