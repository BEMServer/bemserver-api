"""Users API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import User

from bemserver_api import AutoSchema, Schema


class UserSchema(AutoSchema):
    class Meta:
        table = User.__table__
        exclude = ("_is_active", "_is_admin")

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    email = ma.fields.Email(required=True, validate=ma.validate.Length(1, 80))
    password = msa.auto_field(validate=ma.validate.Length(1, 80), load_only=True)
    is_admin = ma.fields.Boolean(dump_only=True)
    is_active = ma.fields.Boolean(dump_only=True)


class UserQueryArgsSchema(Schema):
    name = ma.fields.Str()
    email = ma.fields.Str()
    is_admin = ma.fields.Boolean()
    is_active = ma.fields.Boolean()


class BooleanValueSchema(Schema):
    value = ma.fields.Boolean()
