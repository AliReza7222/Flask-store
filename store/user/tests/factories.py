from factory import Faker, alchemy

from store.extensions import db
from store.user.models import User


class UserFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session

    email = Faker("email")
    password = Faker("password")
