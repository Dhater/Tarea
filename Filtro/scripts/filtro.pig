-- Cargar desde HDFS (usa ruta relativa dentro de HDFS)
raw = LOAD '/pig/input/eventos.csv' USING PigStorage(',')
       AS (uuid:chararray, country:chararray, city:chararray,
           type:chararray, subtype:chararray, street:chararray,
           speed:int, confidence:int, x:float, y:float, pubMillis:long, pub_date:chararray);

-- Filtrado limpio, elimina cabecera y filas con datos nulos o vacíos
limpios = FILTER raw BY
    uuid != 'uuid' AND
    (uuid IS NOT NULL AND TRIM(uuid) != '') AND
    (country IS NOT NULL AND TRIM(country) != '') AND
    (city IS NOT NULL AND TRIM(city) != '') AND
    (type IS NOT NULL AND TRIM(type) != '') AND
    (subtype IS NOT NULL AND TRIM(subtype) != '') AND
    (street IS NOT NULL AND TRIM(street) != '') AND
    (x IS NOT NULL) AND (y IS NOT NULL) AND (pubMillis IS NOT NULL) AND
    (pub_date IS NOT NULL AND TRIM(pub_date) != '');

-- Guardar solo los datos limpios filtrados en HDFS para que otros scripts los usen
STORE limpios INTO '/pig/output/filtrados' USING PigStorage(',');
