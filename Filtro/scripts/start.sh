#!/bin/bash
/usr/sbin/sshd
# Borrar la carpeta /pig/output antes de ejecutar
rm -rf /pig/output
mkdir -p /pig/input
pig -x mapreduce /pig/scripts/filtro.pig || echo 'Fall� Pig filtro'
pig -x mapreduce /pig/scripts/ciudad.pig || echo 'Fall� Pig ciudad an�lisis'
pig -x mapreduce /pig/scripts/tipo.pig || echo 'Fall� Pig tipo an�lisis'
pig -x mapreduce /pig/scripts/fecha.pig || echo 'Fall� Pig fecha an�lisis'
tail -f /dev/null
