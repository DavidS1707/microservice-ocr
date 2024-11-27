FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar los archivos necesarios
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Configurar variables de entorno para AWS
ENV AWS_ACCESS_KEY_ID=<TU_ACCESS_KEY_ID>
ENV AWS_SECRET_ACCESS_KEY=<TU_SECRET_ACCESS_KEY>

EXPOSE 5000

CMD ["python", "app.py"]
