import uuid
from datetime import datetime, timedelta
from http import HTTPStatus

from flask import jsonify, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from store.enums import OrderStatusEnum
from store.extensions import db
from store.order.models import Item, Order
from store.order.schemas import OrderSchema
from store.product.models import Product
from store.routes import create_blueprint_api
from store.user.models import User
from store.utils import calculate_total_price_products

blueprint = create_blueprint_api(name="order", url_prefix="orders", version="v1")


@blueprint.route("/")
class AddOrder(MethodView):  # Real Project this section session or temp memory.
    @blueprint.arguments(OrderSchema)
    @blueprint.response(HTTPStatus.CREATED, OrderSchema)
    @jwt_required()
    def post(self, data):
        add_order_schema = OrderSchema()
        valid_data = add_order_schema.load(data)
        map_products = self.get_map_products(items=valid_data.get("items"))
        calculate_total_price_order = calculate_total_price_products(
            map_products,
            valid_data.get("items"),
        )
        user = User.query.filter_by(email=get_jwt_identity()).first()
        order = self.create_order(add_order_schema, user, calculate_total_price_order)
        db.session.add(order)
        db.session.flush()
        self.create_order_items(order, valid_data.get("items"), map_products)
        db.session.commit()
        return jsonify(add_order_schema.dump(order)), HTTPStatus.CREATED

    def get_map_products(self, items):
        product_ids = [item.get("product_id") for item in items]
        products = (
            db.session.query(
                Product.id,
                Product.price,
                Product.inventory,
            )
            .filter(Product.id.in_(product_ids))
            .all()
        )
        return {product.id: product for product in products}

    def create_order_items(self, order, items, map_products):
        item_objects = [
            Item(
                order_id=order.id,
                product_id=product.id,
                quantity=item.get("quantity"),
                product_price=product.price,
            )
            for item in items
            if (product := map_products.get(item.get("product_id")))
        ]
        db.session.bulk_save_objects(item_objects)

    def create_order(self, add_order_schema, user, calculate_total_price_order):
        order_data = {
            "user_id": user.id,
            "total_price": calculate_total_price_order,
            "tracking_code": str(uuid.uuid4()),
        }
        return add_order_schema.create_order(order_data)


@blueprint.route("/")
class GetListOrder(MethodView):
    @blueprint.response(HTTPStatus.OK, OrderSchema)
    @blueprint.paginate()
    @jwt_required()
    def get(self, pagination_parameters):
        order_schema = OrderSchema()
        pagination = self.pagination_list_order()
        response = self.response(pagination, order_schema)
        return jsonify(response), HTTPStatus.OK

    def pagination_list_order(self):
        page = int(request.args.get("page", 1))
        per_page = 5
        return (
            Order.query.options(joinedload(Order.items))
            .join(User)  # Inner Join
            .filter(User.email == get_jwt_identity())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

    def response(self, pagination, order_schema):
        return {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_orders": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "orders": [order_schema.dump(order) for order in pagination.items],
        }


@blueprint.route("/tracking/<string:tracking_code>")
class GetOrderUser(MethodView):
    @blueprint.response(HTTPStatus.OK, OrderSchema)
    @jwt_required()
    def get(self, tracking_code):
        order_schema = OrderSchema()
        order = Order.query.filter_by(tracking_code=tracking_code).first()

        if not order:
            return jsonify(
                {"error": "User don't have this order."},
            ), HTTPStatus.NOT_FOUND
        return jsonify(order_schema.dump(order)), HTTPStatus.OK


@blueprint.route("/<int:order_id>")
class DeletePendingOrder(MethodView):
    @jwt_required()
    def delete(self, order_id):
        order = (
            Order.query.join(User)
            .filter(User.email == get_jwt_identity(), Order.id == order_id)
            .first()
        )

        if not order:
            return jsonify(
                {"error": f"You don't have any order with ID {order_id}."},
            ), HTTPStatus.NOT_FOUND

        if order.status != OrderStatusEnum.PENDING.name:
            return jsonify(
                {
                    "error": "Your order is not in 'Pending' status and cannot be deleted.",  # noqa: E501
                },
            ), HTTPStatus.FORBIDDEN

        db.session.delete(order)
        db.session.commit()
        return jsonify(
            {
                "message": f"Order with ID {order_id} successfully deleted.",
            },
        ), HTTPStatus.OK


class BaseOrderStatusView(MethodView):
    current_status = None
    new_status = None
    update_inventory = None

    @blueprint.response(HTTPStatus.OK, OrderSchema)
    @jwt_required()
    def patch(self, order_id):
        order = self.get_order(order_id, get_jwt_identity())

        if not order:
            return jsonify(
                {
                    "error": f"You don't have any {self.current_status.lower()} order with ID {order_id}.",  # noqa: E501
                },
            ), HTTPStatus.NOT_FOUND

        products_map = self.get_map_products(order.items)
        self.update_inventory_products(
            order.items,
            self.update_inventory,
            products_map,
        )
        self.update_order_status(order, self.new_status)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Please try again."}), HTTPStatus.CONFLICT

        return jsonify(
            {"message": f"Order with ID {order_id} {self.new_status.lower()}."},
        ), HTTPStatus.OK

    def get_order(self, order_id, identity_user):
        return (
            Order.query.join(User)
            .filter(
                User.email == identity_user,
                Order.id == order_id,
                Order.status == self.current_status,
            )
            .first()
        )

    def get_map_products(self, items):
        products = (
            Product.query.filter(Product.id.in_([item.product_id for item in items]))
            .with_for_update()
            .all()
        )
        return {product.id: product for product in products}

    def update_inventory_products(self, items, update_inventory, products_map):
        for item in items:
            product = products_map.get(item.product_id)
            product.inventory = update_inventory(product.inventory, item.quantity)

    def update_order_status(self, order, new_order_status):
        order.status = self.new_status


@blueprint.route("/<int:order_id>/confirmed")
class ConfirmedOrder(BaseOrderStatusView):
    current_status = OrderStatusEnum.PENDING.name
    new_status = OrderStatusEnum.CONFIRMED.name
    update_inventory = staticmethod(lambda inventory, quantity: inventory - quantity)


@blueprint.route("/<int:order_id>/canceled")
class CanceledOrder(BaseOrderStatusView):
    current_status = OrderStatusEnum.CONFIRMED.name
    new_status = OrderStatusEnum.CANCELED.name
    update_inventory = staticmethod(lambda inventory, quantity: inventory + quantity)


@blueprint.route("/<int:order_id>/completed")
class CompletedOrder(MethodView):
    def patch(self, order_id):
        order = self.get_order(order_id)
        order.status = OrderStatusEnum.COMPLETED.name
        db.session.commit()
        return jsonify(
            {"message": f"Order with ID {order_id} completed."},
        ), HTTPStatus.OK

    def get_order(self, order_id):
        order = Order.query.filter(
            Order.id == order_id,
            Order.status == OrderStatusEnum.CONFIRMED.name,
        ).first()

        if not order:
            return jsonify(
                {"error": f"Don't have any confirmed order with ID {order_id}."},
            ), HTTPStatus.NOT_FOUND
        return order


@blueprint.route("/<int:order_id>")
class PendingOrderUpdateAPI(MethodView):
    decorators = (jwt_required(),)

    @blueprint.arguments(OrderSchema)
    @blueprint.response(HTTPStatus.OK, OrderSchema)
    @jwt_required()
    def put(self, data, order_id):
        condition_date_update_order = self.condition_date_update_order()
        order = self.get_order(order_id, condition_date_update_order)

        if not order:
            return jsonify(
                {
                    "error": f"Order with ID {order_id} is not found, cannot be updated, or is too old.",  # noqa: E501
                },
            ), HTTPStatus.NOT_FOUND

        order_schema = OrderSchema()
        valid_data_order = order_schema.load(data)
        map_products = self.get_map_products(valid_data_order.get("items"))

        calculate_total_price_order = calculate_total_price_products(
            map_products,
            valid_data_order.get("items"),
        )
        self.update_order_items(
            order,
            valid_data_order.get("items"),
            map_products,
        )
        order.total_price = calculate_total_price_order
        db.session.commit()

        return jsonify(order_schema.dump(order)), HTTPStatus.OK

    def condition_date_update_order(self):
        return datetime.now() - timedelta(hours=1)  # noqa: DTZ005

    def get_order(self, order_id, condition_date):
        return (
            Order.query.options(joinedload(Order.items, innerjoin=True))
            .join(User)
            .filter(
                User.email == get_jwt_identity(),
                Order.id == order_id,
                Order.status == OrderStatusEnum.PENDING.name,
                Order.created_at >= condition_date,
            )
            .first()
        )

    def get_map_products(self, items):
        product_ids = [item.get("product_id") for item in items]
        products = (
            db.session.query(Product.id, Product.price, Product.inventory)
            .filter(Product.id.in_(product_ids))
            .all()
        )

        return {product.id: product for product in products}

    def update_order_items(self, order, items, map_products):
        Item.query.filter_by(order_id=order.id).delete()
        item_objects = [
            Item(
                order_id=order.id,
                product_id=product.id,
                quantity=item.get("quantity"),
                product_price=product.price,
            )
            for item in items
            if (product := map_products.get(item.get("product_id")))
        ]
        db.session.bulk_save_objects(item_objects)
