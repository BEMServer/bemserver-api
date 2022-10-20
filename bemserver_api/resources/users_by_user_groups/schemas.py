"""Users by user groups API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import UserByUserGroup

from bemserver_api import AutoSchema, Schema


class UserByUserGroupSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = UserByUserGroup

    id = msa.auto_field(dump_only=True)


class UserByUserGroupQueryArgsSchema(Schema):
    user_id = ma.fields.Int()
    user_group_id = ma.fields.Int()
