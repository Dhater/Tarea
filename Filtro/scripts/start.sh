#!/bin/bash
/usr/sbin/sshd
# Borrar la carpeta /pig/output antes de ejecutar
rm -rf /pig/output
mkdir -p /pig/input
pig -x mapreduce /pig/scripts/filtro.pig || echo 'Falló Pig filtro'
pig -x mapreduce /pig/scripts/ciudad.pig || echo 'Falló Pig ciudad análisis'
pig -x mapreduce /pig/scripts/tipo.pig || echo 'Falló Pig tipo análisis'
pig -x mapreduce /pig/scripts/fecha.pig || echo 'Falló Pig fecha análisis'
tail -f /dev/null
