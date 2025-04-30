FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema para psycopg2 y Redis
RUN apt-get update && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]