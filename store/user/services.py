from http import HTTPStatus

from flask import abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)
from marshmallow import ValidationError

from store.extensions import db
from store.user.models import User
from store.user.schemas import LoginUserSchema, RegisterUserSchema
from store.validators import exists_row


class UserService:
    def register_user(self, user_data: dict) -> dict:
        register_user_schema = RegisterUserSchema()
        valid_data: dict = register_user_schema.load(user_data)
        user: User = register_user_schema.create_user(data=valid_data)

        if exists_row(User, email=user.email):
            msg_error = f"User with email {user.email} already exists."
            raise ValidationError(msg_error)

        db.session.add(user)
        db.session.commit()
        return register_user_schema.dump(user)

    def login_user(self, user_data: dict) -> dict:
        login_user_schema = LoginUserSchema()
        valid_data: dict = login_user_schema.load(user_data)
        user: User | None = User.query.filter_by(email=valid_data.get("email")).first()

        if not user or not user.check_password(valid_data.get("password")):
            abort(
                HTTPStatus.NOT_FOUND,
                description="email or password is invalid!",
            )
        return {
            "access_token": create_access_token(identity=user.email),
            "refresh_token": create_refresh_token(identity=user.email),
        }

    def refresh_token(self) -> str:
        identity: str = get_jwt_identity()
        return create_access_token(identity=identity)

    def detail_user(self) -> dict:
        user: User | None = User.query.filter_by(email=get_jwt_identity()).first()
        if not user:
            abort(HTTPStatus.NOT_FOUND, description="No exists this user!")
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "active": user.active,
            "is_admin": user.is_admin,
        }
