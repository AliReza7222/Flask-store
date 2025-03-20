import uuid
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from store.enums import OrderStatusEnum
from store.extensions import db
from store.order.models import Item, Order
from store.permissions import admin_required
from store.product.models import Product
from store.user.models import User
from store.utils import calculate_total_price_products, to_dict
from store.validators import validate_order_items

blueprint = Blueprint("order", __name__, url_prefix="/api/v1/orders")


@blueprint.route("/", methods=["POST"])
@jwt_required()
def add_order():  # Real Project this section is in Cache or session or temp memory.
    """
    Expected data:

    {
        "items": [
            {
                "product_id": <int>,
                "quantity": <int>
            },
            ...
        ]
    }
    """
    data = request.get_json()
    items = data.get("items", [])

    if not items or not isinstance(items, list):
        return jsonify(
            {"error": "Field 'items' is required and must be a list."},
        ), HTTPStatus.BAD_REQUEST

    if not validate_order_items(items):
        return jsonify(
            {
                "error": "Each item must have an integer 'product_id' and 'quantity'.",
            },
        ), HTTPStatus.BAD_REQUEST

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

    dict_products = {product.id: product for product in products}
    calculate_total_price = calculate_total_price_products(dict_products, items)

    if errors := calculate_total_price.get("errors"):
        return jsonify({"errors": errors}), HTTPStatus.BAD_REQUEST

    user = User.query.filter_by(email=get_jwt_identity()).first()
    order = Order(
        user_id=user.id,
        total_price=calculate_total_price.get("total_price"),
        tracking_code=str(uuid.uuid4()),
    )
    db.session.add(order)
    db.session.flush()

    item_objects = [
        Item(
            order_id=order.id,
            product_id=product.id,
            quantity=item.get("quantity"),
            product_price=product.price,
        )
        for item in items
        if (product := dict_products.get(item.get("product_id")))
    ]
    db.session.bulk_save_objects(item_objects)
    response = to_dict(order)
    response["items"] = [to_dict(item_obj) for item_obj in item_objects]
    db.session.commit()
    return jsonify(response), HTTPStatus.CREATED


@blueprint.route("/tracking/<string:tracking_code>", methods=["GET"])
@jwt_required()
def get_order(tracking_code):
    order = Order.query.filter_by(tracking_code=tracking_code).first()
    if not order:
        return jsonify({"error": "Tracking Code InValid."}), HTTPStatus.NOT_FOUND
    response = to_dict(order)
    response["items"] = [to_dict(item) for item in order.items]
    return jsonify(response), HTTPStatus.OK


@blueprint.route("/", methods=["GET"])
@jwt_required()
def get_list_order():
    page = int(request.args.get("page", 1))
    per_page = 5
    pagination = (
        Order.query.join(User)  # Inner Join
        .filter(User.email == get_jwt_identity())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    response = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_orders": pagination.total,
        "total_pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
        "orders": [to_dict(order) for order in pagination.items],
    }
    return jsonify(response), HTTPStatus.OK


@blueprint.route("/<int:order_id>", methods=["DELETE"])
@jwt_required()
def delete_pending_order(order_id):
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
            {"error": "Your order is not in 'Pending' status and cannot be deleted."},
        ), HTTPStatus.FORBIDDEN
    db.session.delete(order)
    db.session.commit()
    return jsonify(
        {
            "message": f"Order with ID {order_id} successfully deleted.",
        },
    ), HTTPStatus.OK


@blueprint.route("/<int:order_id>/confirmed", methods=["PATCH"])
@jwt_required()
def confirmed_order(order_id):
    order = (
        Order.query.join(User)
        .filter(
            User.email == get_jwt_identity(),
            Order.id == order_id,
            Order.status == OrderStatusEnum.PENDING.name,
        )
        .first()
    )
    if not order:
        return jsonify(
            {"error": f"You don't have any pending order with ID {order_id}."},
        ), HTTPStatus.NOT_FOUND

    items = order.items
    # using of with_for_update for lock row
    # https://www.restack.io/p/sqlalchemy-knowledge-with-for-update-example-cat-ai
    products = (
        Product.query.filter(Product.id.in_([item.product_id for item in items]))
        .with_for_update()
        .all()
    )
    products_mapp = {product.id: product for product in products}
    for item in items:
        product = products_mapp.get(item.product_id)
        if item.quantity > product.inventory:
            return jsonify(
                {
                    "errors": f"Product {product.id} has insufficient stock: {product.inventory} available.",  # noqa: E501
                },
            ), HTTPStatus.BAD_REQUEST
        product.inventory = product.inventory - item.quantity
    order.status = OrderStatusEnum.CONFIRMED.name
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Please try again."}), HTTPStatus.CONFLICT
    return jsonify({"message": f"Order with ID {order_id} confirmed."}), HTTPStatus.OK


@blueprint.route("/<int:order_id>/completed", methods=["PATCH"])
@admin_required()
def completed_order(user, order_id):
    order = Order.query.filter(
        Order.id == order_id,
        Order.status == OrderStatusEnum.CONFIRMED.name,
    ).first()
    if not order:
        return jsonify(
            {"error": f"Don't have any confirmed order with ID {order_id}."},
        ), HTTPStatus.NOT_FOUND
    order.status = OrderStatusEnum.COMPLETED.name
    db.session.commit()
    return jsonify({"message": f"Order with ID {order_id} completed."}), HTTPStatus.OK
