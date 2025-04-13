from http import HTTPStatus

from flask import jsonify, request
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from store.extensions import db
from store.routes import create_blueprint_api
from store.user.models import User
from store.user.schemas import LoginUserSchema, RegisterUserSchema
from store.validators import exists_row

blueprint = create_blueprint_api(name="users", url_prefix="/users", version="v1")


@blueprint.route("/")
class RegisterUserAPI(MethodView):
    @blueprint.arguments(RegisterUserSchema)
    @blueprint.response(HTTPStatus.CREATED, RegisterUserSchema)
    def post(self, user_data):
        register_user_schema = RegisterUserSchema()
        valid_data = register_user_schema.load(user_data)
        user = register_user_schema.create_user(data=valid_data)

        if exists_row(User, email=user.email):
            return jsonify(
                {"error": f"User with email {user.email} already exists."},
            ), HTTPStatus.BAD_REQUEST

        db.session.add(user)
        db.session.commit()
        return jsonify(register_user_schema.dump(user)), HTTPStatus.CREATED


@blueprint.route("/login")
class LoginUserAPI(MethodView):
    @blueprint.arguments(LoginUserSchema)
    def post(self):
        login_user_schema = LoginUserSchema()
        valid_data = login_user_schema.load(request.get_json())
        user = User.query.filter_by(email=valid_data.get("email")).first()

        if not user or not user.check_password(valid_data.get("password")):
            return jsonify(
                {"error": "email or password is invalid!"},
            ), HTTPStatus.NOT_FOUND

        response = {
            "access_token": create_access_token(identity=user.email),
            "refresh_token": create_refresh_token(identity=user.email),
        }
        return jsonify(response), HTTPStatus.OK


@blueprint.route("/refresh")
class RefreshTokenAPI(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token)


@blueprint.route("/<int:user_id>")
class UserDetailAPI(MethodView):
    @blueprint.response(HTTPStatus.OK)
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        response = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "active": user.active,
            "is_admin": user.is_admin,
        }
        return jsonify(response), HTTPStatus.OK
