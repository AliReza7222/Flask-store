import uuid
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from store.extensions import db
from store.order.models import Item, Order
from store.product.models import Product
from store.user.models import User
from store.utils import calculate_total_price_products, to_dict
from store.validators import validate_order_items

blueprint = Blueprint("order", __name__, url_prefix="/api/v1/orders")


@blueprint.route("/", methods=["POST"])
@jwt_required()
def add_order():
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
