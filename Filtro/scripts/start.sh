#!/bin/bash
/usr/sbin/sshd

# Borrar la carpeta /pig/output antes de ejecutar
rm -rf /pig/output

mkdir -p /pig/input

pig -x local /pig/scripts/filtro.pig || echo 'Falló Pig filtro'
pig -x local /pig/scripts/analizar.pig || echo 'Falló Pig análisis'

tail -f /dev/null
