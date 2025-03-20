from sqlalchemy import event, inspect

from store.enums import OrderStatusEnum
from store.extensions import db
from store.order.models import Item, Order
from store.product.models import Product


@event.listens_for(Product, "after_update")
def update_items_and_order_on_product_update(mapper, connection, target):
    """
    Update Items and Pending Order total_price
    """
    # https://stackoverflow.com/questions/29921260/tracking-model-changes-in-sqlalchemy
    state = inspect(target)
    history_product_price = state.get_history("price", True)  # noqa: FBT003

    if not history_product_price.has_changes():
        return

    pending_order_items = (
        Item.query.join(Order)
        .filter(
            Item.product_id == target.id,
            Order.status == OrderStatusEnum.PENDING.name,
        )
        .all()
    )
    order_ids = [item.order_id for item in pending_order_items]
    orders = Order.query.filter(Order.id.in_(order_ids)).all()

    for item, order in zip(pending_order_items, orders, strict=False):
        old_total = item.product_price * item.quantity
        new_total = target.price * item.quantity

        item.product_price = target.price
        order.total_price = order.total_price - old_total + new_total

    db.session.bulk_save_objects(pending_order_items)
    db.session.bulk_save_objects(orders)
