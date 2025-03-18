from email_validator import EmailNotValidError, validate_email


def validate_email_format(email):
    try:
        return bool(validate_email(email, check_deliverability=True).email)
    except EmailNotValidError:
        return None
