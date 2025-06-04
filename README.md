Sistema de Extracción, Filtrado y Análisis de Datos de Tráfico (Waze)

Este proyecto se realiza un flujo de procesamiento de datos basado en contenedores Docker, en donde todo el procesamiento, desde la recolección de datos hasta el análisis final ocurre automáticamente al levantar los servicios.

1.- El scrapper web obtiene datos de tráfico desde la API de Waze.

2.- Los datos son guardados y compartidos mediante un volumen con el filtro de datos (Apache Hadoop y con Pig).

3.- El filtro limpia y transforma los datos, generando un CSV limpio en carpeta output.

4.- Finalmente, el analizador de datos toma ese CSV y produce resultados procesados y organizados.


Todo esto sucede al levantar los contenedores de docker.

Pasos para usarlo:

1. Clonar el repositorio:
   git clone https://github.com/Dhater/Tarea.git
   cd repositorio

2. Levantar todo con Docker(se requiere tener Docker instalado y abierto):

   docker-compose up --build

3.- Todo el pipeline se ejecutará automáticamente:

- El scraper comenzará a obtener eventos de Waze.
- Los eventos se escribirán en shared/input/.
- Hadoop/Pig tomará esos datos, los limpiará y los guardará como CSV en shared/output/.
- El analizador leerá los datos filtrados y mostrará los resultados.


Resultado esperado

Después de levantar los servicios, encontrarás el archivo CSV limpio en:

shared/output/fatos_filtrados.csv
