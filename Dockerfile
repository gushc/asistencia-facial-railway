FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar requirements primero
COPY requirements.txt .

# Instalar dlib PRIMERO con versión específica
RUN pip install --no-cache-dir --timeout 600 dlib==19.22.0

# Instalar el resto de dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY . .

# Exponer puerto
EXPOSE 10000

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
