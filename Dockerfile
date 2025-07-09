# Usa una imagen base con Python
FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000
# El script se montará con volumen, así que no lo copiamos aquí

# Mantiene el contenedor vivo
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]