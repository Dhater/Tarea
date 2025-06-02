#!/bin/bash

# Iniciar servicio SSH, necesario para Hadoop
service ssh start

# Iniciar HDFS (sistema de archivos distribuido)
start-dfs.sh

# Iniciar YARN (gestor de recursos y tareas)
start-yarn.sh

# Esperar un poco para que los servicios estén arriba
sleep 10

# Ejecutar tu script Pig en modo MapReduce
igp -x mapreduce /pig/scripts/filtro.pig

# Mantener el contenedor activo para que no se cierre
tail -f /dev/null
