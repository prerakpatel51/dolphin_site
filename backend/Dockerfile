FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput || true
EXPOSE 8000
CMD ["gunicorn", "dolphin.wsgi:application", "-b", "0.0.0.0:8000", "-w", "3", "--access-logfile", "-"]
