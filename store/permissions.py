from functools import wraps
from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required


def admin_required():
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            from store.user.models import User

            user = User.query.filter_by(email=get_jwt_identity()).first()
            if not user or not user.is_admin:
                return jsonify({"error": "Unauthorized"}), HTTPStatus.UNAUTHORIZED
            kwargs["user"] = user
            return func(*args, **kwargs)

        return wrapper

    return decorator
