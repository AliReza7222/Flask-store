from sqlalchemy.ext.hybrid import hybrid_property

from store.extensions import bcrypt, db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    _password = db.Column(db.LargeBinary(128), nullable=True)
    active = db.Column(db.Boolean(), default=False)
    is_admin = db.Column(db.Boolean(), default=False)
    full_name = db.Column(db.String(150), nullable=True)
    created_products = db.relationship(
        "Product",
        foreign_keys="[Product.created_by]",
        backref="creator",
        lazy=True,
    )
    updated_products = db.relationship(
        "Product",
        foreign_keys="[Product.updated_by]",
        backref="updater",
        lazy=True,
    )
    orders = db.relationship(
        "Order",
        foreign_keys="[Order.user_id]",
        backref="user",
        lazy=True,
    )

    @hybrid_property
    def password(self):
        """Hashed password."""
        return self._password

    @password.setter
    def password(self, value):
        """Set password."""
        self._password = bcrypt.generate_password_hash(value)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self._password, value)

    def __repr__(self):
        return f"<User {self.email}>"
