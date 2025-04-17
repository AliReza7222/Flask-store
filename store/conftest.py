import pytest

from store.app import create_app
from store.extensions import db as _db
from store.user.tests.factories import UserFactory


class TestingConfig:
    TESTING = True
    DEBUG = False
    SECRET_KEY = "testing-secret-key"  # noqa: S105
    JWT_SECRET_KEY = "testing-jwt-secret"  # noqa: S105
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_ECHO = False
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    API_TITLE = "Test Store Management API"
    API_VERSION = "test-1.0.0"
    OPENAPI_VERSION = "3.0.3"


@pytest.fixture
def app():
    app = create_app(config_obj=TestingConfig)

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def db(app):
    _db.drop_all()
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()


@pytest.fixture
def user_store(db):
    user = UserFactory(password="123")  # noqa: S106
    db.session.commit()
    return user
