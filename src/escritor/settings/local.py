"""Local settings overrides. Not tracked in git."""
from .dev import *  # noqa: F401,F403

DEBUG = True
SECRET_KEY = "local-dev-secret-key-do-not-use-in-production"
ALLOWED_HOSTS = ["*"]
