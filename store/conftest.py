import pytest
from flask_jwt_extended import create_access_token

from store.app import create_app
from store.extensions import db as _db
from store.factories import OrderFactory, OrderItemFactory, ProductFactory, UserFactory
from store.settings import REDIS_URL


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
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL


@pytest.fixture
def app():
    app = create_app(config_obj=TestingConfig)

    with app.app_context():  # teardown clear
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
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(db):
    user = UserFactory(is_admin=True)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_headers():
    def _get_access_token(user):
        access_token = create_access_token(identity=user.email)
        return {
            "Authorization": f"Bearer {access_token}",
        }

    return _get_access_token


@pytest.fixture
def product(db):
    product = ProductFactory()
    db.session.add(product)
    db.session.commit()
    return product


@pytest.fixture
def product_factory(db):
    def _create_product(**kwargs):
        product = ProductFactory(**kwargs)
        db.session.add(product)
        db.session.commit()
        return product

    return _create_product


@pytest.fixture
def order_factory(db):
    def _create_order(*args, is_flush=False, **kwargs):
        order = OrderFactory(**kwargs)
        db.session.add(order)
        if is_flush:
            db.session.flush()
        else:
            db.session.commit()
        return order

    return _create_order


@pytest.fixture
def order_item_factory(db):
    def _create_order_item(**kwargs):
        order_item = OrderItemFactory(**kwargs)
        db.session.add(order_item)
        return order_item

    return _create_order_item
