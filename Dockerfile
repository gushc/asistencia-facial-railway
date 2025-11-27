FROM python:3.9-slim

WORKDIR /app

# Dependencias mínimas para dlib wheel
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instalar dlib desde wheel (NO compilar)
RUN pip install --no-cache-dir \
    https://files.pythonhosted.org/packages/1a/42/f0e418cbff496d5f95c1deac1f1e099f3996bd6f66a701d89f5cb918416f/dlib-19.17.0-cp39-cp39-manylinux1_x86_64.whl

# Instalar el resto
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
# Build optimized with dlib wheel - 11/27/2025 02:47:05
