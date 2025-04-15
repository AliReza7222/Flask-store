from http import HTTPStatus

from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended import (
    jwt_required,
)

from store.routes import create_blueprint_api
from store.user.schemas import LoginUserSchema, RegisterUserSchema
from store.user.services import UserService

blueprint = create_blueprint_api(name="users", url_prefix="users", version="v1")
user_service = UserService()


@blueprint.route("/")
class RegisterUserAPI(MethodView):
    @blueprint.arguments(RegisterUserSchema)
    @blueprint.response(HTTPStatus.CREATED, RegisterUserSchema)
    def post(self, data):
        return jsonify(user_service.register_user(data)), HTTPStatus.CREATED


@blueprint.route("/login")
class LoginUserAPI(MethodView):
    @blueprint.arguments(LoginUserSchema)
    def post(self, data):
        return jsonify(user_service.login_user(data)), HTTPStatus.OK


@blueprint.route("/refresh")
class RefreshTokenAPI(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        return jsonify(access_token=user_service.refresh_token()), HTTPStatus.OK


@blueprint.route("/me")
class UserDetailAPI(MethodView):
    @blueprint.response(HTTPStatus.OK)
    @jwt_required()
    def get(self):
        return user_service.detail_user()
