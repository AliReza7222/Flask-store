from marshmallow import Schema, ValidationError, validates

from store.product.models import Product


class ProductSchema(Schema):
    class Meta:
        model = Product
        fields = (
            "name",
            "price",
            "description",
            "inventory",
        )
        required = {
            "name": True,
            "price": True,
            "description": True,
            "inventory": True,
        }

    @validates("price")
    def validate_price(self, data, **kwargs):
        if data < 0:
            raise ValidationError("Price must be a positive number.")  # noqa: TRY003, EM101

    @validates("inventory")
    def validate_inventory(self, data, **kwargs):
        if data < 0:
            raise ValidationError("Inventory must be a non-negative integer.")  # noqa: TRY003, EM101

    def create_product(self, data):
        return Product(**data)
