import datetime

from store.enums import OrderStatusEnum
from store.extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(50), default=OrderStatusEnum.PENDING.value)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    total_price = db.Column(db.Float, nullable=False)
    tracking_code = db.Column(db.String(40), nullable=False)
    items = db.relationship(
        "Item",
        foreign_keys="[Item.order_id]",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Order(status={self.status},user={self.user_id})"


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Item(order_id={self.order_id}, product_id={self.product_id})>"
