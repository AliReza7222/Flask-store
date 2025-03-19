def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


def calculate_total_price_products(dict_products, items):
    errors = []
    total_price = 0

    for item in items:
        product_id = item.get("product_id")
        product = dict_products.get(product_id)
        quantity = item.get("quantity")

        if not product:
            errors.append(f"Product with id {product_id} not found.")
        elif product.inventory < quantity:
            errors.append(
                f"""
                    Product {product_id} has
                    insufficient stock: {product.inventory} available.
                """,
            )
        else:
            total_price += quantity * product.price

    return (
        {"total_price": total_price, "errors": errors}
        if errors
        else {"total_price": total_price}
    )
