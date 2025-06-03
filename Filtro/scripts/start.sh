#!/bin/bash
/usr/sbin/sshd

# Borrar la carpeta /pig/output antes de ejecutar
rm -rf /pig/output

mkdir -p /pig/input

pig -x local /pig/scripts/filtro.pig || echo 'Falló Pig filtro'
pig -x local /pig/scripts/ciudad.pig || echo 'Falló Pig ciudad análisis'
pig -x local /pig/scripts/tipo.pig || echo 'Falló Pig tipo análisis'
pig -x local /pig/scripts/fecha.pig || echo 'Falló Pig fecha análisis'

tail -f /dev/null
