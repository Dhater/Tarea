-- Cargar los datos filtrados
datos = LOAD '/pig/output/filtrados' USING PigStorage(',')
        AS (uuid:chararray, country:chararray, city:chararray,
            type:chararray, subtype:chararray, street:chararray,
            speed:int, confidence:int, x:float, y:float, pubMillis:long);

-- Agrupar por ciudad
grp_ciudad = GROUP datos BY city;

-- Contar eventos por ciudad
conteo_ciudad = FOREACH grp_ciudad GENERATE
                  group AS ciudad,
                  COUNT(datos) AS total_eventos;

-- Guardar resultados
STORE conteo_ciudad INTO '/pig/output/por_ciudad' USING PigStorage(',');
