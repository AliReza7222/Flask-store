from getpass import getpass

import click
from email_validator import EmailNotValidError, validate_email

from store.extensions import db
from store.user.models import User


@click.command()
def create_admin_user():
    email = input("Please enter your email: ")

    try:
        valid = validate_email(email, check_deliverability=True)
        email = valid.email
    except EmailNotValidError as e:
        print(f"Invalid email: {e}")  # noqa: T201
        return

    # checking the existence of a user with this email
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print("This email is already registered!")  # noqa: T201
        return

    password = getpass("Please enter your password: ")
    admin_user = User(email=email, is_admin=True, active=True)
    admin_user.password = password

    db.session.add(admin_user)
    db.session.commit()
    print("admin user created successfully!")  # noqa: T201
