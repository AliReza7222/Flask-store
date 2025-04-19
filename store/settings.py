"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""

from datetime import timedelta

from celery.schedules import crontab
from environs import Env

env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"
SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL", default="sqlite:///db.sqlite3")
SECRET_KEY = env.str("SECRET_KEY")
JWT_SECRET_KEY = env.str("JWT_SECRET_KEY")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
BCRYPT_LOG_ROUNDS = env.int("BCRYPT_LOG_ROUNDS", default=13)
SQLALCHEMY_ECHO = DEBUG
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
# Config swagger for flask-smorest
API_TITLE = "Store Management API"
API_VERSION = "1.0.0"
OPENAPI_VERSION = "3.0.3"
OPENAPI_URL_PREFIX = "/"
OPENAPI_SWAGGER_UI_PATH = "/apidocs"
OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
API_SPEC_OPTIONS = {
    "components": {
        "securitySchemes": {
            "Bearer Auth": {
                "type": "apiKey",
                "name": "Authorization",
                "bearerFormat": "JWT",
                "in": "header",
                "description": "Enter your JWT token like: **Bearer &lt;token>**",
            },
        },
    },
    "security": [{"Bearer Auth": []}],
}
# Config celery
REDIS_URL = env.str("REDIS_URL", default="redis://localhost:6379/0")
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default=REDIS_URL)
CELERY_BEAT_SCHEDULE = {
    "remove-pending-order-after-one-hour": {
        "task": "store.tasks.remove_old_order_pending_status",
        "schedule": crontab(minute="*/5"),
    },
}
