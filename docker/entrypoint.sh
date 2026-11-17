#!/bin/sh
set -e

DB="${DATA_DIR:-/data}/db.sqlite3"

if [ ! -w "${DATA_DIR:-/data}" ]; then
    echo "Error: ${DATA_DIR:-/data} is not writable by uid $(id -u)." >&2
    echo "Run 'chown $(id -u):$(id -g)' on the host directory, or set UID/GID in .env." >&2
    exit 1
fi

if [ -f "$DB" ]; then
    FIRST_RUN=0
else
    FIRST_RUN=1
fi

python manage.py migrate --noinput

if [ "$FIRST_RUN" = "1" ]; then
    echo "* First run: loading initial data"
    python manage.py loaddata initial_database.json
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        python manage.py createsuperuser --noinput
    else
        echo "* No DJANGO_SUPERUSER_USERNAME/PASSWORD set, create an admin with:"
        echo "  docker compose exec compteur python manage.py createsuperuser"
    fi
fi

exec gunicorn compteur.wsgi \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --access-logfile - \
    --error-logfile -
