from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from store.extensions import db
from store.user.models import User

blueprint = Blueprint("user", __name__, url_prefix="/api/v1/users")


@blueprint.route("/", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name", "")

    if not email or not password:
        return jsonify(
            {"error": "Please enter email and password."},
        ), HTTPStatus.BAD_REQUEST

    if len(password) < 8:  # noqa: PLR2004
        return jsonify(
            {"error": "Password must be at least 8 characters long."},
        ), HTTPStatus.BAD_REQUEST

    if db.session.query(User.query.filter_by(email=email).exists()).scalar():
        return jsonify(
            {"error": f"User with email {email} already exists."},
        ), HTTPStatus.BAD_REQUEST

    user = User(email=email, active=True, full_name=full_name)
    user.password = password
    db.session.add(user)
    db.session.commit()
    response = {
        "id": user.id,
        "email": email,
        "full_name": full_name,
    }
    return jsonify(response), HTTPStatus.CREATED


@blueprint.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    response = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "active": user.active,
        "is_admin": user.is_admin,
    }
    return jsonify(response), HTTPStatus.OK


@blueprint.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify(
            {"error": "Please enter email and password."},
        ), HTTPStatus.BAD_REQUEST

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "email or password is invalid!"}), HTTPStatus.NOT_FOUND

    response = {
        "access_token": create_access_token(identity=user.email),
        "refresh_token": create_refresh_token(identity=user.email),
    }
    return jsonify(response), HTTPStatus.OK


@blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
