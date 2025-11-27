FROM python:3.9-slim

# Dependencias necesarias para dlib precompilado
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Instala dlib sin compilar si hay wheel disponible
RUN pip install --no-cache-dir --prefer-binary dlib \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
