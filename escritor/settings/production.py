"""Production settings."""
from .base import *  # noqa: F401,F403

DEBUG = False
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "escritor"),
        "USER": os.environ.get("POSTGRES_USER", "escritor"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
