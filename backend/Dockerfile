FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput || true
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/media /app/staticfiles \
    && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
ENV GUNICORN_WORKERS=1
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn dolphin.wsgi:application -b [::]:${PORT:-8000} -w ${GUNICORN_WORKERS} --access-logfile /dev/null --error-logfile -"]
