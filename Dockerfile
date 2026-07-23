# syntax=docker/dockerfile:1

# Imagen base ligera de Python 3.11
FROM python:3.11-slim

# Evita que Python escriba archivos .pyc en disco y asegura que los logs salgan directamente a consola
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    PORT=5000

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python aprovechando el caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente de la aplicación
COPY . .

# Exponer el puerto 5000 para el servicio web
EXPOSE 5000

# Comando de inicio usando el servidor WSGI de producción (Gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]