# 🚦 Sistema de Extracción, Filtrado y Análisis de Datos de Tráfico (Waze)

Este proyecto implementa un **pipeline de procesamiento de datos** totalmente automatizado mediante **contenedores Docker**. Desde la recolección hasta el análisis final, todo ocurre al levantar los servicios definidos.

## 🧩 Componentes del sistema

1. **Scraper Web**
   Obtiene eventos de tráfico en tiempo real desde la API de **Waze**.

2. **Volumen Compartido**
   Los datos obtenidos son guardados y compartidos con el siguiente módulo mediante un volumen Docker.

3. **Filtro de Datos (Apache Hadoop + Pig)**
   Limpia y transforma los datos. El resultado es un archivo en formato **Pig Storage** guardado en `data/output/filtrados/`.

4. **Analizador de Datos**
   Procesa los datos limpios y genera resultados estructurados por **tipo**, **ciudad** y **fecha** en `data/output/por_{Categoria}/`.

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

   docker-compose up -d
   ```

3. **Pipeline en acción:**

   * El scraper comenzará a recolectar eventos de Waze.
   * Los eventos se guardarán en `shared/input/`.
   * Hadoop/Pig los filtrará y transformará, guardando el resultado limpio como Pig Storage en `shared/data/output/filtrados`.
   * El analizador procesará los datos limpios y mostrará estadísticas organizadas.

---

## 📁 Archivos de salida esperados

Después de ejecutar el pipeline, encontrarás los resultados en:

* **Archivo limpio filtrado:**
  `Filtro/data/output/filtrados/part-m-00000`

* **Datos analizados:**

  * Por fecha: `Filtro/data/output/por_fecha/part-r-00000`
  * Por tipo: `Filtro/data/output/por_tipo/part-r-00000`
  * Por ciudad: `Filtro/data/output/por_ciudad/part-r-00000`

---

## 📝 Notas finales

Este sistema permite automatizar el flujo completo de análisis de datos de tráfico urbano desde su extracción hasta su análisis final, facilitando la obtención de insights relevantes sin intervención manual.
