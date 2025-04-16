import uuid
from datetime import datetime, timedelta
from http import HTTPStatus

from flask import abort
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, joinedload

from store.enums import OrderStatusEnum
from store.exceptions import ConflictIntegrityError
from store.extensions import db
from store.order.models import Item, Order
from store.order.schemas import OrderSchema
from store.product.models import Product
from store.user.models import User
from store.utils import calculate_total_price_products


class OrderService:
    def add_order(self, data: dict) -> dict:
        add_order_schema = OrderSchema()
        valid_data: dict = add_order_schema.load(data)
        map_products: dict = self.get_map_products(
            items=valid_data.get("items"),
            fields=(Product.id, Product.price, Product.inventory),
            lock=False,
        )
        calculate_total_price_order: float = calculate_total_price_products(
            map_products,
            valid_data.get("items"),
        )
        user: User = User.query.filter_by(email=get_jwt_identity()).first()
        order: Order = self.create_order(
            add_order_schema,
            user,
            calculate_total_price_order,
        )
        db.session.add(order)
        db.session.flush()
        self.create_order_items(order, valid_data.get("items"), map_products)
        db.session.commit()
        return add_order_schema.dump(order)

    def get_map_products(
        self,
        items: dict,
        *args,
        lock: bool,
        fields: tuple | None = None,
    ) -> dict:
        product_ids: list = [item.get("product_id") for item in items]
        if fields:
            query: Query = db.session.query(*fields)
        else:
            query: Query = Product.query

        query = query.filter(Product.id.in_(product_ids))

        if lock:
            query = query.with_for_update()

        products = query.all()

        return {product.id: product for product in products}

    def create_order_items(self, order: Order, items: list, map_products: dict) -> None:
        item_objects = [
            Item(
                order_id=order.id,
                product_id=product.id,
                quantity=item.get("quantity"),
                product_price=product.price,
            )
            for item in items
            if (product := map_products.get(item.get("product_id")))
        ]
        db.session.bulk_save_objects(item_objects)

    def create_order(
        self,
        add_order_schema: OrderSchema,
        user: User,
        calculate_total_price_order: float,
    ) -> Order:
        order_data: dict = {
            "user_id": user.id,
            "total_price": calculate_total_price_order,
            "tracking_code": str(uuid.uuid4()),
        }
        return add_order_schema.create_order(order_data)

    def list_products(self, page_number: int) -> dict:
        order_schema = OrderSchema()
        pagination = self.pagination_list_order(page_number)
        return {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_orders": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "orders": [order_schema.dump(order) for order in pagination.items],
        }

    def pagination_list_order(self, page_number: int):
        return (
            Order.query.options(joinedload(Order.items))
            .join(User)  # Inner Join
            .filter(User.email == get_jwt_identity())
            .paginate(page=page_number, per_page=5, error_out=False)
        )

    def order(self, tracking_code: uuid) -> dict:
        order_schema = OrderSchema()
        order = self.find_order(tracking_code=tracking_code)
        return order_schema.dump(order)

    def find_order(
        self,
        tracking_code: uuid.UUID | None = None,
        order_id: int | None = None,
        status: str | None = None,
    ) -> Order | None:
        if tracking_code:
            query = Order.query.filter_by(tracking_code=tracking_code)

        elif order_id:
            query = Order.query.join(User).filter(
                User.email == get_jwt_identity(),
                Order.id == order_id,
            )
            if status:
                query = query.filter(Order.status == status)

        order = query.first()
        if not order:
            abort(
                HTTPStatus.NOT_FOUND,
                description="User don't have this order.",
            )

        return order

    def delete(self, order_id: int) -> dict:
        order = self.find_order(order_id=order_id)

        if order.status != OrderStatusEnum.PENDING.name:
            abort(
                HTTPStatus.FORBIDDEN,
                description="Your order is not in 'Pending' status and cannot be deleted.",  # noqa: E501
            )

        db.session.delete(order)
        db.session.commit()
        return {
            "message": f"Order with ID {order_id} successfully deleted.",
        }

    def update_inventory_products(
        self,
        items: list,
        products_map: dict,
        new_status: str,
    ) -> None:
        for item in items:
            product = products_map.get(item.product_id)
            product.inventory = self.calculate_inventory_products(
                product.inventory,
                item.quantity,
                new_status,
            )

    def change_order_status(self, order: Order, new_order_status: str) -> None:
        order.status = new_order_status

    def completed_order(
        self,
        order_id: int,
        current_status: str,
        new_status: str,
    ) -> dict:
        order: Order = self.find_order(order_id=order_id, status=current_status)
        self.change_order_status(order, new_status)
        db.session.commit()
        return {"message": f"Order with ID {order_id} completed."}

    def update_order_status(
        self,
        order_id: int,
        current_status: str,
        new_status: str,
    ) -> dict:
        order_schema = OrderSchema()
        order = self.find_order(order_id=order_id, status=current_status)
        data_order = order_schema.dump(order)
        products_map = self.get_map_products(items=data_order.get("items"), lock=True)
        self.update_inventory_products(order.items, products_map, new_status)
        self.change_order_status(order, new_status)

        try:
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            msg_error = "An error occurred, try again later."
            raise ConflictIntegrityError(msg_error) from err

        return {"message": f"Order with ID {order_id} {new_status.lower()}."}

    def calculate_inventory_products(
        self,
        product_inventory: int,
        item_quentity: int,
        new_status: str,
    ) -> int:
        result = None
        if new_status == OrderStatusEnum.CONFIRMED.name:
            result = product_inventory - item_quentity
        if new_status == OrderStatusEnum.CANCELED.name:
            result = product_inventory + item_quentity
        return result

    def full_update_order(self, data: dict, order_id: int) -> dict:
        order = self.find_order(order_id=order_id, status=OrderStatusEnum.PENDING.name)
        if order.created_at <= self.condition_date_update_order():
            abort(
                HTTPStatus.NOT_FOUND,
                description=f"Order with ID {order_id} is not found, cannot be updated, or is too old.",  # noqa: E501
            )

        order_schema = OrderSchema()
        valid_data_order = order_schema.load(data)
        map_products: dict = self.get_map_products(
            items=valid_data_order.get("items"),
            fields=(Product.id, Product.price, Product.inventory),
            lock=False,
        )

        calculate_total_price_order = calculate_total_price_products(
            map_products,
            valid_data_order.get("items"),
        )
        self.update_order_items(
            order,
            valid_data_order.get("items"),
            map_products,
        )
        order.total_price = calculate_total_price_order
        db.session.commit()
        return order_schema.dump(order)

    def update_order_items(self, order: Order, items: list, map_products: dict) -> None:
        Item.query.filter_by(order_id=order.id).delete()
        item_objects = [
            Item(
                order_id=order.id,
                product_id=product.id,
                quantity=item.get("quantity"),
                product_price=product.price,
            )
            for item in items
            if (product := map_products.get(item.get("product_id")))
        ]
        db.session.bulk_save_objects(item_objects)

    def condition_date_update_order(self):
        return datetime.now() - timedelta(hours=1)  # noqa: DTZ005
