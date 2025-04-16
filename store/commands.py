from getpass import getpass

import click

from store.extensions import db
from store.user.models import User
from store.validators import validate_email_format


@click.command()
def create_admin_user() -> None:
    email: str = input("Please enter your email: ")

    if not validate_email_format(email):
        print("Invalid email.")  # noqa: T201
        return

    # checking the existence of a user with this email
    existing_user: User | None = User.query.filter_by(email=email).first()
    if existing_user:
        print("This email is already registered!")  # noqa: T201
        return

    password: str = getpass("Please enter your password: ")
    admin_user: User = User(email=email, is_admin=True, active=True)
    admin_user.password = password

    db.session.add(admin_user)
    db.session.commit()
    print("admin user created successfully!")  # noqa: T201
