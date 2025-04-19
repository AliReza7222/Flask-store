from http import HTTPStatus

from flask import jsonify
from flask.views import MethodView

from store.permissions import admin_required
from store.product.schemas import ProductSchema
from store.product.services import ProductService
from store.routes import create_blueprint_api

blueprint = create_blueprint_api(name="products", url_prefix="products", version="v1")
product_service = ProductService()


@blueprint.route("/")
class AddProduct(MethodView):
    @blueprint.arguments(ProductSchema)
    @blueprint.response(HTTPStatus.CREATED, ProductSchema)
    @admin_required()
    def post(self, data, user):
        return jsonify(product_service.add_product(data, user)), HTTPStatus.CREATED


@blueprint.route("/")
class GetListProducts(MethodView):
    @blueprint.response(HTTPStatus.OK, ProductSchema)
    @blueprint.paginate()
    def get(self, pagination_parameters):
        return jsonify(product_service.list_products()), HTTPStatus.OK


@blueprint.route("/<int:product_id>")
class GetProduct(MethodView):
    @blueprint.response(HTTPStatus.OK, ProductSchema)
    def get(self, product_id):
        return jsonify(product_service.product(product_id)), HTTPStatus.OK


@blueprint.route("/<int:product_id>")
class DeleteProduct(MethodView):
    @admin_required()
    def delete(self, product_id, *args, **kwargs):
        product_service.delete(product_id)
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
    def put(self, data, product_id, user):
        return jsonify(
            product_service.full_update(data, product_id, user),
        ), HTTPStatus.OK
