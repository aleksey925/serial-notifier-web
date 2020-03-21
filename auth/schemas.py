from marshmallow import Schema, fields, validate

from models import SEX


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=3))


class RegistrationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    sex = fields.String(validate=validate.OneOf(choices=SEX), allow_none=True)
    nick = fields.String(
        required=True,
        validate=validate.Length(min=3, max=50)
    )
    name = fields.String(validate=validate.Length(max=50), allow_none=True)
    surname = fields.String(validate=validate.Length(max=50), allow_none=True)
