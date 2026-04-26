FROM python:3.11-slim

WORKDIR /app

COPY Configuration/requirements.txt /app/Configuration/requirements.txt
RUN pip install --no-cache-dir -r /app/Configuration/requirements.txt

COPY . /app

WORKDIR /app
CMD ["python", "Main Application/main.py"]
