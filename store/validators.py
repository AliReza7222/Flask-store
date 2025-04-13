from email_validator import EmailNotValidError, validate_email

from store.extensions import db


def validate_email_format(email):
    try:
        return bool(validate_email(email, check_deliverability=True).email)
    except EmailNotValidError:
        return None


def exists_row(model, **kwargs):
    return db.session.query(model.query.filter_by(**kwargs).exists()).scalar()
