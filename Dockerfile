FROM python:3.9-slim

ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

CMD exec gunicorn app.main:app \
--bind :$PORT \
--workers 1 \
--worker-class uvicorn.workers.UvicornWorker \
--threads 8 \
--timeout 0
