"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""

from datetime import timedelta

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
SWAGGER = {
    "swagger": "2.0",
    "info": {
        "title": "Store Management API",
        "description": "API documentation for the store management system",
        "version": "1.0.0",
    },
    "schemes": ["http", "https"],
    "hosts": ["127.0.0.1:5000", "localhost:5000"],
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter 'Bearer <your_token>' in the field below",
        },
    },
}
