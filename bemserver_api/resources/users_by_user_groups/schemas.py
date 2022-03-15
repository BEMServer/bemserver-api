"""Users by user groups API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import UserByUserGroup

from bemserver_api import AutoSchema


class UserByUserGroupSchema(AutoSchema):
    class Meta:
        table = UserByUserGroup.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class UserByUserGroupQueryArgsSchema(ma.Schema):
    user_id = ma.fields.Int()
    user_group_id = ma.fields.Int()
