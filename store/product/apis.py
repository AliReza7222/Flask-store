from http import HTTPStatus

from flask import Blueprint, jsonify, request

from store.extensions import db
from store.permissions import admin_required
from store.product.models import Product

blueprint = Blueprint("product", __name__, url_prefix="/api/v1/products")


@blueprint.route("/", methods=["POST"])
@admin_required()
def add_product(user):
    data = request.get_json()
    required_fields = ("name", "price", "inventory")
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify(
            {
                "error": f"Missiong Fields: {', '.join(missing_fields)}",
            },
        ), HTTPStatus.BAD_REQUEST

    if not isinstance(data.get("price"), (int, float)) or data.get("price") <= 0:
        return jsonify(
            {"error": "Price must be a positive number."},
        ), HTTPStatus.BAD_REQUEST

    if not isinstance(data.get("inventory"), int) or data.get("inventory") < 0:
        return jsonify(
            {"error": "Inventory must be a non-negative integer."},
        ), HTTPStatus.BAD_REQUEST

    product_data = {
        "name": data.get("name"),
        "price": data.get("price"),
        "inventory": data.get("inventory"),
        "created_by": user.id,
        "description": data.get("description", ""),
    }
    product = Product(**product_data)
    db.session.add(product)
    db.session.commit()
    product_data.update({"id": product.id, "created_at": product.created_at})
    return jsonify(product_data), HTTPStatus.CREATED
