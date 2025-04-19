from datetime import datetime, timedelta
from http import HTTPStatus

from store.enums import OrderStatusEnum
from store.order.models import Order
from store.product.models import Product


class TestOrderApi:
    def test_add_order(self, client, db, auth_headers, user_store, product_factory):
        headers = auth_headers(user_store)
        product1 = product_factory(name="P1", price=99.99, inventory=1)
        product2 = product_factory(name="P2", price=45.01, inventory=2)

        order_data = {
            "items": [
                {
                    "product_id": product1.id,
                    "quantity": 1,
                },
                {
                    "product_id": product2.id,
                    "quantity": 1,
                },
            ],
        }

        response = client.post("api/v1/orders/", json=order_data, headers=headers)
        response_data = response.get_json()
        total_price = product1.price + product2.price

        assert response.status_code == HTTPStatus.CREATED
        assert response_data.get("total_price", 0) == total_price

    def test_add_order_insufficient_inventory(
        self,
        client,
        db,
        auth_headers,
        user_store,
        product_factory,
    ):
        product = product_factory(inventory=1)

        headers = auth_headers(user_store)
        order_data = {
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 5,
                },
            ],
        }

        response = client.post("api/v1/orders/", json=order_data, headers=headers)
        data = response.get_json()
        errors = data.get("errors", [])

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert errors
        assert "insufficient stock" in errors[0]

    def test_add_order_nonexistent_product(self, client, db, auth_headers, user_store):
        headers = auth_headers(user_store)
        order_data = {
            "items": [
                {
                    "product_id": 999999,
                    "quantity": 1,
                },
            ],
        }

        response = client.post("api/v1/orders/", json=order_data, headers=headers)
        data = response.get_json()
        errors = data.get("errors", [])

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert errors
        assert "id 999999 not found" in errors[0]

    def test_delete_pending_order(
        self,
        client,
        user_store,
        order_factory,
        auth_headers,
    ):
        order = order_factory(user_id=user_store.id)
        order_id = order.id
        headers = auth_headers(user_store)

        response = client.delete(f"/api/v1/orders/{order.id}", headers=headers)

        assert response.status_code == HTTPStatus.OK
        assert Order.query.get(order_id) is None

    def test_delete_non_pending_order(
        self,
        client,
        user_store,
        order_factory,
        auth_headers,
    ):
        order = order_factory(
            user_id=user_store.id,
            status=OrderStatusEnum.CONFIRMED.name,
        )
        order_id = order.id
        headers = auth_headers(user_store)

        response = client.delete(f"/api/v1/orders/{order.id}", headers=headers)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert Order.query.get(order_id) is not None

    def test_confirm_order_updates_inventory_and_status(  # noqa: PLR0913
        self,
        db,
        client,
        order_factory,
        product_factory,
        auth_headers,
        user_store,
        order_item_factory,
    ):
        order = order_factory(user_id=user_store.id, is_flush=True)
        product1 = product_factory(inventory=5)
        product2 = product_factory(inventory=10)
        item1 = order_item_factory(
            product=product1,
            quantity=2,
            product_price=product1.price,
        )
        item2 = order_item_factory(
            product=product2,
            quantity=9,
            product_price=product2.price,
        )
        order.items = [item1, item2]
        expected_product1_inventory = product1.inventory - item1.quantity
        expected_product2_inventory = product2.inventory - item2.quantity
        db.session.commit()
        headers = auth_headers(user_store)

        response = client.patch(f"/api/v1/orders/{order.id}/confirmed", headers=headers)

        assert response.status_code == HTTPStatus.OK

        updated_order = Order.query.get(order.id)
        updated_product1 = Product.query.get(item1.product_id)
        updated_product2 = Product.query.get(item2.product_id)

        assert updated_order.status == OrderStatusEnum.CONFIRMED.name
        assert updated_product1.inventory == expected_product1_inventory
        assert updated_product2.inventory == expected_product2_inventory

    def test_canceled_order_updates_inventory_and_status(  # noqa: PLR0913
        self,
        db,
        client,
        order_factory,
        product_factory,
        auth_headers,
        user_store,
        order_item_factory,
    ):
        order = order_factory(
            user_id=user_store.id,
            status=OrderStatusEnum.CONFIRMED.name,
            is_flush=True,
        )
        product1 = product_factory(inventory=5)
        product2 = product_factory(inventory=10)
        item1 = order_item_factory(
            product=product1,
            quantity=2,
            product_price=product1.price,
        )
        item2 = order_item_factory(
            product=product2,
            quantity=9,
            product_price=product2.price,
        )
        order.items = [item1, item2]
        expected_product1_inventory = product1.inventory + item1.quantity
        expected_product2_inventory = product2.inventory + item2.quantity
        db.session.commit()
        headers = auth_headers(user_store)

        response = client.patch(f"/api/v1/orders/{order.id}/canceled", headers=headers)

        assert response.status_code == HTTPStatus.OK

        updated_order = Order.query.get(order.id)
        updated_product1 = Product.query.get(item1.product_id)
        updated_product2 = Product.query.get(item2.product_id)

        assert updated_order.status == OrderStatusEnum.CANCELED.name
        assert updated_product1.inventory == expected_product1_inventory
        assert updated_product2.inventory == expected_product2_inventory

    def test_completed_order_status(
        self,
        client,
        auth_headers,
        order_factory,
        user_store,
    ):
        order = order_factory(
            user_id=user_store.id,
            status=OrderStatusEnum.CONFIRMED.name,
        )
        headers = auth_headers(user_store)

        response = client.patch(f"/api/v1/orders/{order.id}/completed", headers=headers)
        updated_order = Order.query.get(order.id)

        assert response.status_code == HTTPStatus.OK
        assert updated_order.status == OrderStatusEnum.COMPLETED.name

    def test_update_pending_order_with_new_items(  # noqa: PLR0913
        self,
        client,
        product_factory,
        order_factory,
        order_item_factory,
        auth_headers,
        user_store,
    ):
        product1 = product_factory(inventory=10, price=20)
        product2 = product_factory(inventory=15, price=30)
        product3 = product_factory(inventory=25, price=50)

        order = order_factory(
            user_id=user_store.id,
            created_at=datetime.now(),  # noqa: DTZ005
        )

        order_item_factory(
            order_id=order.id,
            product_id=product1.id,
            quantity=2,
            product_price=product1.price,
        )
        order_item_factory(
            order_id=order.id,
            product_id=product2.id,
            quantity=1,
            product_price=product2.price,
        )
        headers = auth_headers(user_store)
        data = {
            "items": [
                {"product_id": product1.id, "quantity": 1},
                {"product_id": product3.id, "quantity": 2},
            ],
        }

        response = client.put(f"/api/v1/orders/{order.id}", json=data, headers=headers)
        order = Order.query.get(order.id)
        expected_total_price_order = (1 * product1.price) + (2 * product3.price)
        expected_order_items = [item.product_id for item in order.items]

        assert response.status_code == HTTPStatus.OK
        assert order.total_price == expected_total_price_order
        assert [product1.id, product3.id] == expected_order_items

    def test_update_order_too_old_fails(  # noqa: PLR0913
        self,
        client,
        product_factory,
        order_factory,
        order_item_factory,
        auth_headers,
        user_store,
    ):
        old_time = datetime.now() - timedelta(hours=2)  # noqa: DTZ005
        product = product_factory()
        order = order_factory(user_id=user_store.id, created_at=old_time)
        headers = auth_headers(user_store)
        data = {
            "items": [{"product_id": product.id, "quantity": 1}],
        }

        response = client.put(f"/api/v1/orders/{order.id}", json=data, headers=headers)

        assert response.status_code == HTTPStatus.NOT_FOUND
