from http import HTTPStatus

from flask import jsonify, request
from flask.views import MethodView

from store.extensions import db
from store.permissions import admin_required
from store.product.models import Product
from store.product.schemas import ProductSchema
from store.routes import create_blueprint_api
from store.validators import exists_row

blueprint = create_blueprint_api(name="products", url_prefix="products", version="v1")


@blueprint.route("/")
class AddProduct(MethodView):
    @blueprint.arguments(ProductSchema)
    @blueprint.response(HTTPStatus.CREATED, ProductSchema)
    @admin_required()
    def post(self, data, *args, **kwargs):
        add_product_schema = ProductSchema()
        valid_data = add_product_schema.load(data)
        product = add_product_schema.create_product(valid_data)

        if exists_row(Product, name=valid_data.get("name")):
            return jsonify(
                {
                    "error": f"Product with this name {valid_data.get('name')} already exists.",  # noqa: E501
                },
            ), HTTPStatus.BAD_REQUEST

        db.session.add(product)
        db.session.commit()
        return jsonify(add_product_schema.dump(product)), HTTPStatus.CREATED


@blueprint.route("/")
class GetListProducts(MethodView):
    @blueprint.response(HTTPStatus.OK, ProductSchema)
    @blueprint.paginate()
    def get(self, pagination_parameters):
        product_schema = ProductSchema()
        # https://flask-sqlalchemy.readthedocs.io/en/stable/api/#flask_sqlalchemy.pagination.Pagination
        page = int(
            request.args.get("page", 1),
        )  # default is "1" and for ex: /?page=<number>
        per_page = 10
        pagination = Product.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
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


@blueprint.route("/<int:product_id>")
class GetProduct(MethodView):
    @blueprint.response(HTTPStatus.OK, ProductSchema)
    def get(self, product_id):
        product = Product.query.get_or_404(product_id)
        product_schema = ProductSchema()
        return jsonify(product_schema.dump(product)), HTTPStatus.OK


@blueprint.route("/<int:product_id>")
class DeleteProduct(MethodView):
    @admin_required()
    def delete(self, product_id, *args, **kwargs):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify(
            {
                "message": f"Product with ID {product_id} successfully deleted.",
            },
        ), HTTPStatus.OK


@blueprint.route("/<int:product_id>")
class UpdateProduct(MethodView):
    @blueprint.arguments(ProductSchema)
    @blueprint.response(HTTPStatus.OK, ProductSchema)
    @admin_required()
    def put(self, data, product_id, user, *args, **kwargs):
        update_product_schema = ProductSchema()
        valid_data = update_product_schema.load(data)

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
