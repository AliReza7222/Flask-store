from http import HTTPStatus

from store.order.models import Order
from store.product.models import Product


class TestProductApi:
    def test_add_product(self, client, db, admin_user, auth_headers):
        headers = auth_headers(admin_user)
        data = {
            "name": "New Product",
            "price": 19.99,
            "description": "Test description",
            "inventory": 10,
        }
        response = client.post("api/v1/products/", json=data, headers=headers)
        product = Product.query.filter_by(name=data.get("name", "New Product")).first()

        assert response.status_code == HTTPStatus.CREATED
        assert product is not None
        assert product.name == data.get("name", "New Product")
        assert product.created_by == admin_user.id

    def test_add_product_with_duplicate_name(
        self,
        client,
        db,
        admin_user,
        auth_headers,
        product,
    ):
        headers = auth_headers(admin_user)
        duplicate_name_product = product.name
        data = {
            "name": duplicate_name_product,
            "price": 25.50,
            "description": "First product",
            "inventory": 5,
        }
        client.post("api/v1/products/", json=data, headers=headers)
        response = client.post("api/v1/products/", json=data, headers=headers)
        count_products = Product.query.filter_by(name=product.name).count()

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert count_products == 1

    def test_add_product_unauthorized_user(self, client, db, user_store, auth_headers):
        headers = auth_headers(user_store)
        data = {
            "name": "Unauthorized Product",
            "price": 15.00,
            "description": "Should not be created",
            "inventory": 3,
        }

        response = client.post("api/v1/products/", json=data, headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_product_success(
        self,
        client,
        db,
        admin_user,
        auth_headers,
        product,
    ):
        headers = auth_headers(admin_user)
        product_id = product.id
        response = client.delete(f"/api/v1/products/{product_id}", headers=headers)

        assert response.status_code == HTTPStatus.OK
        assert Product.query.get(product_id) is None

    def test_delete_nonexistent_product(self, client, db, admin_user, auth_headers):
        headers = auth_headers(admin_user)
        non_existent_id = 9999

        response = client.delete(f"/api/v1/products/{non_existent_id}", headers=headers)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_product_unauthorized(
        self,
        client,
        user_store,
        auth_headers,
        product,
    ):
        headers = auth_headers(user_store)
        response = client.delete(f"/api/v1/products/{product.id}", headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_full_update_product_successfully(
        self,
        client,
        db,
        admin_user,
        auth_headers,
        product,
    ):
        headers = auth_headers(admin_user)
        update_data = {
            "name": "Updated Product",
            "price": 20.5,
            "description": "Updated description",
            "inventory": 100,
        }

        response = client.put(
            f"/api/v1/products/{product.id}",
            json=update_data,
            headers=headers,
        )
        updated_product = Product.query.get(product.id)

        assert response.status_code == HTTPStatus.OK
        assert updated_product.name == update_data["name"]
        assert updated_product.price == update_data["price"]
        assert updated_product.description == update_data["description"]
        assert updated_product.inventory == update_data["inventory"]
        assert updated_product.updated_by == admin_user.id

    def test_delete_product_in_order_items(  # noqa: PLR0913
        self,
        client,
        product,
        order_item_factory,
        db,
        auth_headers,
        admin_user,
    ):
        order_item_factory(product=product)

        headers = auth_headers(admin_user)

        response = client.delete(f"/api/v1/products/{product.id}", headers=headers)

        assert response.status_code == HTTPStatus.CONFLICT
        assert Product.query.filter_by(id=product.id) is not None

    def test_product_update_reflects_in_order_total_price(  # noqa: PLR0913
        self,
        client,
        db,
        auth_headers,
        order_factory,
        order_item_factory,
        product_factory,
        admin_user,
    ):
        headers = auth_headers(admin_user)
        product1 = product_factory(name="P1", price=99.99, inventory=1)
        product2 = product_factory(name="P2", price=45.01, inventory=2)
        order_items_data = {
            "items": [
                {"product_id": product1.id, "quantity": 1},
                {"product_id": product2.id, "quantity": 2},
            ],
        }

        response_create_order = client.post(
            "/api/v1/orders/",
            headers=headers,
            json=order_items_data,
        )
        data_response_create_order = response_create_order.get_json()
        old_order = Order.query.filter_by(
            id=data_response_create_order.get("id", 0),
        ).first()
        old_calculate_total_price = (product1.price * 1) + (product2.price * 2)

        assert response_create_order.status_code == HTTPStatus.CREATED
        assert old_order is not None
        assert old_order.total_price == old_calculate_total_price

        new_data_product2 = {
            "name": "NEWProduct1",
            "price": 100,
            "inventory": 4,
            "description": "",
        }
        response_update_product = client.put(
            f"/api/v1/products/{product2.id}",
            headers=headers,
            json=new_data_product2,
        )

        new_order = Order.query.filter_by(
            id=data_response_create_order.get("id", 0),
        ).first()
        new_calculate_total_price = (product1.price * 1) + (product2.price * 2)

        assert response_update_product.status_code == HTTPStatus.OK
        assert new_order.total_price == new_calculate_total_price
        assert product2.price == new_data_product2.get("price", 0)
