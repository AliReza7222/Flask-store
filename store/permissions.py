from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from store.user.models import User


def admin_required():
    def decorator(func):
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = User.query.filter_by(email=get_jwt_identity()).first()
            if not user or not user.is_admin:
                return jsonify({"error": "Unauthorized"}), HTTPStatus.UNAUTHORIZED
            return func(user, *args, **kwargs)

        return wrapper

    return decorator
