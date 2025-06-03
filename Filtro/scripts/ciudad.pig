grp_ciudad = GROUP datos BY city;

conteo_ciudad = FOREACH grp_ciudad GENERATE
                  group AS ciudad,
                  COUNT(datos) AS total_eventos;

STORE conteo_ciudad INTO '/pig/output/por_ciudad' USING PigStorage(',');
