#!/bin/sh
set -e

mkdir -p /app/media /app/staticfiles
chown -R appuser:appuser /app/media /app/staticfiles

if [ "$RAILWAY_SERVICE_NAME" = "email-worker" ]; then
  exec su appuser -s /bin/sh -c "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py process_email_queue --sleep 5 --batch-size 100 --workers 5"
fi

exec su appuser -s /bin/sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn dolphin.wsgi:application -b [::]:8000 -w 3 --timeout ${GUNICORN_TIMEOUT:-120} --access-logfile /dev/null --error-logfile -"
