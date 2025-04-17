from http import HTTPStatus

from store.user.models import User


class TestUserApi:
    def test_register_user(self, client):
        data = {
            "email": "TestUser@gmail.com",
            "full_name": "Testuser",
            "password": "test12345",
            "re_password": "test12345",
        }
        response = client.post(
            "/api/v1/users/",
            json=data,
        )
        user = User.query.filter_by(email="TestUser@gmail.com").first()

        assert response.status_code == HTTPStatus.CREATED
        assert user is not None

    def test_register_user_duplicate_email(self, client, db, user_store):
        data = {
            "email": user_store.email,
            "full_name": "Testuser",
            "password": "test12345",
            "re_password": "test12345",
        }
        response = client.post("/api/v1/users/", json=data)

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_login_user(self, client, db, user_store):
        data = {
            "email": user_store.email,
            "password": "123",
        }
        response = client.post("/api/v1/users/login", json=data)
        assert response.status_code == HTTPStatus.OK

    def test_invalid_data_login_user(self, client, db, user_store):
        data = {
            "email": user_store.email,
            "password": "test12345",
        }
        response = client.post("/api/v1/users/login", json=data)
        assert response.status_code == HTTPStatus.NOT_FOUND
