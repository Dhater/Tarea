# 🚦 Sistema de Extracción, Filtrado, Análisis y Visualización de Datos y Tráfico (Waze)

Este proyecto implementa un **pipeline de procesamiento de datos** totalmente automatizado mediante **contenedores Docker**. Desde la recolección hasta la visualización final, todo ocurre al levantar los servicios definidos.

## 🧩 Componentes del sistema

1. **Scraper Web**
   Obtiene eventos de tráfico en tiempo real desde la API de **Waze**.

2. **Volumen Compartido**
   Los datos obtenidos son guardados y compartidos con el siguiente módulo mediante un volumen Docker.

3. **Filtro de Datos (Apache Hadoop + Pig)**
   Limpia y transforma los datos. El resultado es un archivo en formato **Pig Storage** guardado en `data/output/filtrados/`.

4. **Analizador de Datos**
   Procesa los datos limpios y genera resultados estructurados por **tipo**, **ciudad** y **fecha** en `data/output/por_{Categoria}/`.
   
6. **Indexador de Datos**
   Toma los datos estructurados por el analizador y los indexa a una base de datos elasticsearch.

7. **Visualización de Datos**
   Presenta los datos indexados de manera visualmente atractiva, utilizando gráficos y métricas claras.
   
8. **Generador de trafico ElasticSearch**
   Se genera trafico de consultas Elastic para hacer uso de un cache de Redis. 
   
---

## ⚙️ ¿Cómo usarlo?

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/Dhater/Tarea.git
   cd Tarea
   ```

2. **Levantar los servicios con Docker:**

   > ⚠️ Requisitos: Tener **Docker** instalado y ejecutándose. En Windows, se requiere también **WSL**.

   ```bash
   docker-compose up --build
   ```
   ```bash
   docker-compose up -d
   ```

3. **Pipeline en acción:**

   * El scraper comenzará a recolectar eventos de Waze.
   * Los eventos se guardarán en `shared/input/`.
   * Hadoop/Pig los filtrará y transformará, guardando el resultado limpio como Pig Storage en `shared/data/output/filtrados`.
   * El analizador procesará los datos limpios y mostrará estadísticas organizadas.
   * El indexador de datos ingresara los datos a elasticsearch.
   * El visualizador de datos podrá mostrar gráficos gracias a los datos indexados

---

## 📁 Datos indexados esperados.

Luego de indexar los datos se espera ver en el apartado de Index Managment los datos estructurados ya ingresados en elastic, como algo así:

`incidentes_por_ciudad`
`incidentes_por_fecha`
`incidentes_por_tipo`
`incidentes_trafico`

## 📝 Notas finales

Este sistema permite automatizar el flujo completo de análisis de datos de tráfico urbano desde su extracción hasta su análisis final, facilitando la obtención de insights relevantes sin intervención manual.

🛠️ En caso de producirse un error al indexar los datos en Elasticsearch, puedes reiniciar el servicio de indexación ejecutando el siguiente comando en la terminal:

```bash
docker compose restart indexer
```
