from marshmallow import ValidationError

from store.product.models import Product


def _validate_product_for_order(product: Product, quantity: int, product_id: int):
    if not product:
        msg_error = f"Product with id {product_id} not found."
        raise ValidationError(
            msg_error,
            field_name="items",
        )
    if product.inventory < quantity:
        msg_error = f"Product {product_id} has insufficient stock: {product.inventory} available."  # noqa: E501
        raise ValidationError(
            msg_error,
            field_name="items",
        )


def calculate_total_price_products(dict_products, items):
    total_price = 0

    for item in items:
        product_id = item.get("product_id")
        product = dict_products.get(product_id)
        quantity = item.get("quantity")
        _validate_product_for_order(product, quantity, product_id)
        total_price += quantity * product.price

    return total_price
