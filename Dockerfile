FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise

COPY . .
COPY docker/settings_local.py compteur/settings_local.py

RUN BUILD_TIME=1 python manage.py collectstatic --noinput \
    && mkdir -p /data

EXPOSE 8000
ENTRYPOINT ["/app/docker/entrypoint.sh"]
