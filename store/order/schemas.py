from marshmallow import Schema, fields
from marshmallow.validate import Range

from store.order.models import Item, Order


class AddItemSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=Range(min=1))

    def create_item(self, data):
        return Item(**data)


class OrderSchema(Schema):
    items = fields.List(fields.Nested(AddItemSchema), required=True)

    class Meta:
        fields = (
            "id",
            "user_id",
            "status",
            "created_at",
            "total_price",
            "tracking_code",
            "items",
        )
        dump_only = (
            "id",
            "user_id",
            "status",
            "created_at",
            "total_price",
            "tracking_code",
        )

    def create_order(self, data):
        return Order(**data)
