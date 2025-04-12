from http import HTTPStatus

from flasgger import swag_from
from flask import Blueprint, jsonify, request

from store.extensions import db
from store.permissions import admin_required
from store.product.models import Product
from store.product.schemas import ProductSchema
from store.validators import exists_row

blueprint = Blueprint("product", __name__, url_prefix="/products")


@blueprint.route("/", methods=["POST"])
@admin_required()
@swag_from("/store/swagger_docs/product/add_product.yml")
def add_product(user):
    add_product_schema = ProductSchema()
    valid_data = add_product_schema.load(request.get_json())
    product = add_product_schema.create_product(valid_data)

    if Product.query.filter_by(name=valid_data.get("name")).first():
        return jsonify(
            {
                "error": f"Product with this name {valid_data.get('name')} already exists.",  # noqa: E501
            },
        ), HTTPStatus.BAD_REQUEST

    db.session.add(product)
    db.session.commit()
    return jsonify(add_product_schema.dump(product)), HTTPStatus.CREATED


@blueprint.route("/", methods=["GET"])
@swag_from("/store/swagger_docs/product/list_products.yml")
def list_products():
    product_schema = ProductSchema()
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
        "products": [product_schema.dump(product) for product in pagination.items],
    }
    return jsonify(response), HTTPStatus.OK


@blueprint.route("/<int:product_id>", methods=["GET"])
@swag_from("/store/swagger_docs/product/get_product.yml")
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_schema = ProductSchema()
    return jsonify(product_schema.dump(product)), HTTPStatus.OK


@blueprint.route("/<int:product_id>", methods=["DELETE"])
@admin_required()
@swag_from("/store/swagger_docs/product/delete_product.yml")
def delete_product(user, product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify(
        {
            "message": f"Product with ID {product_id} successfully deleted.",
        },
    ), HTTPStatus.OK


@blueprint.route("/<int:product_id>", methods=["PUT"])
@admin_required()
@swag_from("/store/swagger_docs/product/update_product.yml")
def update_product(user, product_id):
    update_product_schema = ProductSchema()
    valid_data = update_product_schema.load(request.get_json())

    if exists_row(Product, name=valid_data.get("name")):
        return jsonify(
            {"error": "Product with this name already exists."},
        ), HTTPStatus.BAD_REQUEST

    # Dirty Update for running event after_update
    product = Product.query.get_or_404(product_id)
    for field, value in valid_data.items():
        setattr(product, field, value)
    product.updated_by = user.id
    db.session.commit()
    return jsonify(update_product_schema.dump(product)), HTTPStatus.OK
