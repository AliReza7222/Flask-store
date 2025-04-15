from marshmallow import Schema, fields
from marshmallow.validate import Range

from store.product.models import Product


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True, validate=Range(min=0))
    description = fields.Str(required=True)
    inventory = fields.Int(required=True, validate=Range(min=1))

    def create_product(self, data):
        return Product(**data)
