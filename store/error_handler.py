from http import HTTPStatus

from flask import jsonify
from marshmallow import ValidationError

from store.exceptions import ConflictIntegrityError


def store_error_handler(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({"errors": error.messages}), HTTPStatus.BAD_REQUEST

    @app.errorhandler(404)
    def handle_not_found_error(error):
        return jsonify({"errors": error.description}), HTTPStatus.NOT_FOUND

    @app.errorhandler(ConflictIntegrityError)
    def handle_conflict_db_error(error):
        return jsonify({"errors": str(error)}), HTTPStatus.CONFLICT
