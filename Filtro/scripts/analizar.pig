-- Cargar datos filtrados desde la salida del primer script
datos = LOAD '/pig/output/filtrados' USING PigStorage(',') 
        AS (uuid:chararray, country:chararray, city:chararray,
            type:chararray, subtype:chararray, street:chararray,
            speed:int, confidence:int, x:float, y:float);

-- Agrupar por ciudad, calle y tipo
grp = GROUP datos BY (city, street, type);

-- Contar la cantidad de eventos en cada grupo
conteos = FOREACH grp GENERATE
            FLATTEN(group) AS (city, street, type),
            COUNT(datos) AS total_eventos;

-- Guardar resultados
STORE conteos INTO '/pig/output/analisis' USING PigStorage(',');
