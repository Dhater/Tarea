-- Carga datos con pub_date como chararray (YYYY-MM-DD)
datos = LOAD '/pig/output/filtrados' USING PigStorage(',')
        AS (uuid:chararray, country:chararray, city:chararray,
            type:chararray, subtype:chararray, street:chararray,
            speed:int, confidence:int, x:float, y:float, pubMillis:long, pub_date:chararray);

-- Agrupa por pub_date (fecha sin hora)
agrupado = GROUP datos BY pub_date;

-- Cuenta eventos por fecha
conteo = FOREACH agrupado GENERATE
            group AS fecha_legible,
            COUNT(datos) AS total_eventos;

-- Guarda resultado con fecha y conteo
STORE conteo INTO '/pig/output/por_fecha' USING PigStorage(',');
