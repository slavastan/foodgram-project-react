FROM python:3.9.7-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install build-essential -y
RUN pip install -r requirements.txt

COPY . .

CMD gunicorn backend.wsgi:application --bind 0.0.0.0:8000