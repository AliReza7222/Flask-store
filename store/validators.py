from email_validator import EmailNotValidError, validate_email


def validate_email_format(email):
    try:
        return bool(validate_email(email, check_deliverability=True).email)
    except EmailNotValidError:
        return None


def validate_order_items(items):
    return all(
        isinstance(item.get("product_id"), int)
        and isinstance(item.get("quantity"), int)
        for item in items
    )
