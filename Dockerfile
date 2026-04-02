FROM python:3.9-slim
WORKDIR /app
# Instalam dependintele
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copiem restul codului
COPY . .
# Comanda de rulare
CMD ["python", "scanner.py"]
