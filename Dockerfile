FROM python:3.9-slim

WORKDIR /app

# Solo dependencias ABSOLUTAMENTE necesarias
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# ESTRATEGIA FREE TIER: Instalar en ORDEN específico
RUN pip install --no-cache-dir --timeout 300 numpy==1.24.3
RUN pip install --no-cache-dir --timeout 600 dlib==19.22.0
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
