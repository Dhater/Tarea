# Sistema Distribuido de Scraping y Caché

Este proyecto utiliza contenedores Docker para desplegar un sistema distribuido que incluye:

- Un scraper que obtiene eventos según coordenadas geográficas (latitud y longitud).
- Un servicio de caché (`cache_service`) que intermedia entre el trafico generado , Redis y PostgreSQL.
- Un servidor de base de datos PostgreSQL.
- Un servicio de caché Redis.
- Un contenedor adicional llamado `trafico` (actualmente no utilizado por problemas de conexión).

## Estructura General

El archivo `docker-compose.yml` crea y configura los siguientes servicios:

### 1. **Scraper**
- Construido desde la carpeta `./scraper` con su respectivo `Dockerfile`.
- Realiza scraping de eventos basándose en latitudes y longitudes predefinidas.
- Envía los datos a la base de datos PostgreSQL y puede interactuar con Redis.
- Utiliza variables de entorno para conectarse a los servicios de base de datos y caché.

### 2. **PostgreSQL**
- Imagen oficial `postgres:16`.
- Servidor de base de datos estándar.
- Usa un volumen persistente (`postgres_data`) y un archivo SQL de inicialización (`init.sql`).
- Expone el puerto `5432` para conexiones externas si se desea.
- Incluye un `healthcheck` para verificar su disponibilidad.

### 3. **Redis**
- Imagen oficial `redis:7`.
- Actúa como un sistema de caché estándar.
- Usa un volumen persistente (`redis_data`) y un `healthcheck` simple con `redis-cli ping`.

### 4. **Cache Service**
- Construido desde la carpeta `./cache_service`.
- Expone una API Flask en el puerto `5000`.
- Recibe solicitudes, consulta Redis o PostgreSQL y responde con los datos correspondientes.
- Está diseñado para crear tráfico regular hacia Redis y PostgreSQL.
- Incluye un endpoint `/health` para verificar su estado.

### 5. **Trafico (No activo)**
- Construido desde la carpeta `./trafico`.
- Su propósito es generar tráfico automático hacia el servicio `cache_service`.
- Actualmente **no se utiliza** debido a problemas de conexión.

## Red y Volúmenes

- Todos los servicios están conectados a una red personalizada `red_scraper`.
- Los datos persistentes de PostgreSQL y Redis se almacenan en los volúmenes `postgres_data` y `redis_data`, respectivamente.

## Cómo usar

1. Asegúrate de tener Docker y Docker Compose instalados.
2. Ejecuta el entorno con:

```bash
docker-compose up --build
