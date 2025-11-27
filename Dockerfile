FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema MÍNIMAS
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar requirements primero
COPY requirements.txt .

# ESTRATEGIA: Instalar numpy PRIMERO (requerido por dlib)
RUN pip install --no-cache-dir numpy==1.24.3

# Instalar dlib con COMPILACIÓN PARALELA
RUN pip install --no-cache-dir --timeout 1200 dlib==19.22.0

# Instalar el resto de dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY . .

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
