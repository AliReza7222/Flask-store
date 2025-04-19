from factory import (
    Faker,
    LazyAttribute,
    SelfAttribute,
    Sequence,
    SubFactory,
    alchemy,
    post_generation,
)

from store.enums import OrderStatusEnum
from store.extensions import db
from store.order.models import Item, Order
from store.product.models import Product
from store.user.models import User


class UserFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session

    email = Faker("email")
    password = Faker("password")


class ProductFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Product
        sqlalchemy_session = db.session

    name = Sequence(lambda n: f"Product {n}")
    price = Faker("pyfloat", left_digits=3, right_digits=2, positive=True)
    description = Faker("sentence")
    inventory = Faker("random_int", min=1, max=100)
    created_at = Faker("date_time_this_year")
    updated_at = Faker("date_time_this_year")


class OrderFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Order
        sqlalchemy_session = db.session

    status = OrderStatusEnum.PENDING.name
    created_at = Faker("date_time_this_year")
    total_price = Faker("pyfloat", left_digits=2, right_digits=2, positive=True)
    tracking_code = Faker("uuid4")

    @post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            total_price = 0
            for item in extracted:
                item.order = self
                db.session.add(item)
                total_price += item.product_price * item.quantity
            self.total_price = total_price


class OrderItemFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Item
        sqlalchemy_session = db.session

    product = SubFactory(ProductFactory)
    product_id = SelfAttribute("product.id")
    product_price = LazyAttribute(lambda obj: obj.product.price)
    order_id = 1
    quantity = 1
