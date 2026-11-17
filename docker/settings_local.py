# Settings used by the Docker image. Everything is configured through
# environment variables; the database and the generated secret key live in
# DATA_DIR, which is meant to be bind-mounted from the host.
import os
import secrets

from .settings import MIDDLEWARE

DATA_DIR = os.environ.get('DATA_DIR', '/data')

DEBUG = os.environ.get('DEBUG', '0') == '1'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, 'db.sqlite3'),
    }
}


def _secret_key():
    if os.environ.get('SECRET_KEY'):
        return os.environ['SECRET_KEY']
    if os.environ.get('BUILD_TIME') == '1':  # collectstatic during docker build
        return 'build-only'
    path = os.path.join(DATA_DIR, 'secret_key')
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(secrets.token_urlsafe(50))
        os.chmod(path, 0o600)
    with open(path) as f:
        return f.read().strip()


SECRET_KEY = _secret_key()

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

# Behind a reverse proxy terminating TLS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files are collected into the image and served by WhiteNoise
STATIC_ROOT = '/app/static'
MIDDLEWARE.insert(MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1,
                  'whitenoise.middleware.WhiteNoiseMiddleware')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': os.environ.get('LOG_LEVEL', 'WARNING')},
}
