-- Dividir pubMillis entre mil y luego entre 86400 para obtener el número de días desde 1970
datos_con_fecha = FOREACH datos GENERATE
                    uuid, city, type, pubMillis,
                    (long)(pubMillis / 1000 / 86400) AS dia;

grp_fecha = GROUP datos_con_fecha BY dia;

conteo_fecha = FOREACH grp_fecha GENERATE
                 group AS fecha_unix,
                 COUNT(datos_con_fecha) AS total_eventos;

STORE conteo_fecha INTO '/pig/output/por_fecha' USING PigStorage(',');
