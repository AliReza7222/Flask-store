from http import HTTPStatus

from flask import jsonify, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from store.enums import OrderStatusEnum
from store.order.schemas import OrderSchema
from store.order.services import OrderService
from store.routes import create_blueprint_api

blueprint = create_blueprint_api(name="order", url_prefix="orders", version="v1")
order_service = OrderService()


@blueprint.route("/")
class AddOrder(MethodView):  # Real Project this section session or temp memory.
    @blueprint.arguments(OrderSchema)
    @blueprint.response(HTTPStatus.CREATED, OrderSchema)
    @jwt_required()
    def post(self, data: dict):
        return jsonify(order_service.add_order(data)), HTTPStatus.CREATED


@blueprint.route("/")
class GetListOrder(MethodView):
    @blueprint.response(HTTPStatus.OK, OrderSchema)
    @blueprint.paginate()
    @jwt_required()
    def get(self, pagination_parameters):
        page_number: int = int(request.args.get("page", 1))
        return jsonify(order_service.list_products(page_number)), HTTPStatus.OK


@blueprint.route("/tracking/<string:tracking_code>")
class GetOrderUser(MethodView):
    @blueprint.response(HTTPStatus.OK, OrderSchema)
    @jwt_required()
    def get(self, tracking_code):
        return jsonify(order_service.order(tracking_code)), HTTPStatus.OK


@blueprint.route("/<int:order_id>")
class DeletePendingOrder(MethodView):
    @jwt_required()
    def delete(self, order_id: int):
        return jsonify(order_service.delete(order_id)), HTTPStatus.OK


@blueprint.route("/<int:order_id>/confirmed")
class ConfirmedOrder(MethodView):
    @blueprint.response(HTTPStatus.OK, OrderSchema)
    @jwt_required()
    def patch(self, order_id: int):
        return jsonify(
            order_service.update_order_status(
                order_id,
                OrderStatusEnum.PENDING.name,
                OrderStatusEnum.CONFIRMED.name,
            ),
        ), HTTPStatus.OK


@blueprint.route("/<int:order_id>/canceled")
class CanceledOrder(MethodView):
    @blueprint.response(HTTPStatus.OK, OrderSchema)
    @jwt_required()
    def patch(self, order_id: int):
        return jsonify(
            order_service.update_order_status(
                order_id,
                current_status=OrderStatusEnum.CONFIRMED.name,
                new_status=OrderStatusEnum.CANCELED.name,
            ),
        ), HTTPStatus.OK


@blueprint.route("/<int:order_id>/completed")
class CompletedOrder(MethodView):
    @blueprint.response(HTTPStatus.OK, OrderSchema)
    @jwt_required()
    def patch(self, order_id: int):
        return jsonify(
            order_service.completed_order(
                order_id,
                OrderStatusEnum.CONFIRMED.name,
                OrderStatusEnum.COMPLETED.name,
            ),
        ), HTTPStatus.OK


@blueprint.route("/<int:order_id>")
class PendingOrderUpdateAPI(MethodView):
    @blueprint.arguments(OrderSchema)
    @blueprint.response(HTTPStatus.OK, OrderSchema)
    @jwt_required()
    def put(self, data: dict, order_id: int):
        return jsonify(order_service.full_update_order(data, order_id)), HTTPStatus.OK
