from marshmallow import Schema, ValidationError, fields, validates_schema
from marshmallow.validate import Email, Length

from store.user.models import User


class RegisterUserSchema(Schema):
    re_password = fields.Str(load_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "email", "full_name", "password", "re_password")
        load_only = ("password",)
        dump_only = ("id",)
        required = {
            "email": True,
            "full_name": True,
            "password": True,
        }
        validate = {
            "email": Email(),
            "full_name": Length(min=1, max=150),
            "password": Length(min=8),
        }

    @validates_schema
    def validate_data(self, data, **kwargs):
        if data.get("password") != data.get("re_password"):
            error_msg = "Passwords do not match."
            raise ValidationError(error_msg, field_name="password")

    def create_user(self, data, **kwargs):
        data.pop("re_password", None)
        user = User(**data)
        user.password = data.get("password")
        return user


class LoginUserSchema(Schema):
    email = fields.Email(required=True, validate=[Email()])
    password = fields.Str(
        required=True,
        load_only=True,
    )
