from http import HTTPStatus

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

    def test_delete_product_in_order_items(self):
        pass

    def test_product_update_reflects_in_order_total_price(self):
        pass
