from http import HTTPStatus

from flask import Blueprint, jsonify, request

from store.extensions import db
from store.permissions import admin_required
from store.product.models import Product
from store.utils import to_dict

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

    if Product.query.filter_by(name=data.get("name")).first():
        return jsonify(
            {"error": f"Product with this name {data.get('name')} already exists."},
        ), HTTPStatus.BAD_REQUEST

    if not isinstance(data.get("price"), (int, float)) or data.get("price") <= 0:
        return jsonify(
            {"error": "Price must be a positive number."},
        ), HTTPStatus.BAD_REQUEST

    if not isinstance(data.get("inventory"), int) or data.get("inventory") < 0:
        return jsonify(
            {"error": "Inventory must be a non-negative integer."},
        ), HTTPStatus.BAD_REQUEST

    product = Product(
        name=data.get("name"),
        price=data.get("price"),
        inventory=data.get("inventory"),
        created_by=user.id,
        description=data.get("description", ""),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(to_dict(product)), HTTPStatus.CREATED


@blueprint.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(to_dict(product)), HTTPStatus.OK


@blueprint.route("/<int:product_id>", methods=["DELETE"])
@admin_required()
def delete_product(user, product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify(
        {
            "message": f"Product with ID {product_id} successfully deleted.",
        },
    ), HTTPStatus.OK
