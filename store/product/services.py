from http import HTTPStatus

from flask import abort, request
from marshmallow import ValidationError

from store.extensions import db
from store.product.models import Product
from store.product.schemas import ProductSchema
from store.user.models import User
from store.validators import exists_row


class ProductService:
    def add_product(self, product_data: dict) -> dict:
        add_product_schema = ProductSchema()
        valid_data: dict = add_product_schema.load(product_data)
        product: Product = add_product_schema.create_product(valid_data)

        if exists_row(Product, name=valid_data.get("name")):
            msg_error = (
                f"Product with this name {valid_data.get('name')} already exists."
            )
            raise ValidationError(msg_error)

        db.session.add(product)
        db.session.commit()
        return add_product_schema.dump(product)

    def list_products(self) -> dict:
        product_schema = ProductSchema()
        # https://flask-sqlalchemy.readthedocs.io/en/stable/api/#flask_sqlalchemy.pagination.Pagination
        page = int(
            request.args.get("page", 1),
        )  # default is "1" and for ex: /?page=<number>
        per_page = 10
        pagination = Product.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
        return {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_products": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "products": [product_schema.dump(product) for product in pagination.items],
        }

    def product(self, product_id: int) -> dict:
        product: Product = self.find_product(product_id)
        product_schema = ProductSchema()
        return product_schema.dump(product)

    def delete(self, product_id: int) -> None:
        product: Product = self.find_product(product_id)
        db.session.delete(product)
        db.session.commit()

    def full_update(self, data: dict, product_id: int, user: User) -> dict:
        update_product_schema = ProductSchema()
        valid_data: dict = update_product_schema.load(data)

        if exists_row(Product, name=valid_data.get("name")):
            raise ValidationError("Product with this name already exists.")  # noqa: TRY003, EM101

        # Dirty Update for running event after_update
        product: Product = self.find_product(product_id)
        for field, value in valid_data.items():
            setattr(product, field, value)
        product.updated_by = user.id
        db.session.commit()
        return update_product_schema.dump(product)

    def find_product(self, product_id: int) -> Product:
        product: Product | None = Product.query.filter_by(id=product_id).first()
        if not product:
            abort(
                HTTPStatus.NOT_FOUND,
                description=f"Product with product_id {product_id} not found.",
            )
        return product
