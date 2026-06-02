#!/bin/sh
set -e

mkdir -p /app/media /app/staticfiles
chown -R appuser:appuser /app/media /app/staticfiles

if [ "$(id -u)" = "0" ]; then
  exec su appuser -s /bin/sh -c "$*"
fi

exec "$@"
