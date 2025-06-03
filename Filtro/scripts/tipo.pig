datos = LOAD '/pig/output/filtrados' USING PigStorage(',') 
        AS (uuid:chararray, country:chararray, city:chararray,
            type:chararray, subtype:chararray, street:chararray,
            speed:int, confidence:int, x:float, y:float, pubMillis:long);

grp_tipo = GROUP datos BY type;

conteo_tipo = FOREACH grp_tipo GENERATE
                group AS tipo,
                COUNT(datos) AS total_eventos;

STORE conteo_tipo INTO '/pig/output/por_tipo' USING PigStorage(',');
