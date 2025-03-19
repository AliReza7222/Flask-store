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
    db.session.flush()
    response = to_dict(product)
    db.session.commit()
    return jsonify(response), HTTPStatus.CREATED


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


@blueprint.route("/", methods=["GET"])
def list_products():
    # https://flask-sqlalchemy.readthedocs.io/en/stable/api/#flask_sqlalchemy.pagination.Pagination
    page = int(
        request.args.get("page", 1),
    )  # default is "1" and for ex: /?page=<number>
    per_page = 10
    pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    response = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_products": pagination.total,
        "total_pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
        "products": [to_dict(product) for product in pagination.items],
    }
    return jsonify(response), HTTPStatus.OK


@blueprint.route("/<int:product_id>", methods=["PUT"])
@admin_required()
def update_product(user, product_id):
    data = request.get_json()
    fields = ("name", "price", "inventory", "description")
    missing_fields = [field for field in fields if field not in data]
    product = Product.query.get_or_404(product_id)
    if missing_fields:
        return jsonify(
            {
                "error": f"Missiong Fields: {', '.join(missing_fields)}",
            },
        ), HTTPStatus.BAD_REQUEST

    if (
        Product.query.filter_by(name=data.get("name")).first()
        and data.get("name") != product.name
    ):
        return jsonify(
            {"error": "Product with this name already exists."},
        ), HTTPStatus.BAD_REQUEST

    for field in fields:
        setattr(product, field, data.get(field))
    product.updated_by = user.id
    db.session.add(product)
    db.session.flush()
    response = to_dict(product)
    db.session.commit()
    return jsonify(response), HTTPStatus.OK
