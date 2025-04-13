from marshmallow import Schema, ValidationError, fields, validates_schema
from marshmallow.validate import Email, Length

from store.user.models import User


class RegisterUserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True, validate=[Email()])
    full_name = fields.Str(required=True, validate=Length(min=1, max=150))
    password = fields.Str(required=True, load_only=True, validate=Length(min=8))
    re_password = fields.Str(required=True, load_only=True)

    @validates_schema
    def validate_data(self, data, **kwargs):
        if data.get("password") != data.get("re_password"):
            raise ValidationError("Passwords do not match.", field_name="password")  # noqa: EM101, TRY003

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
