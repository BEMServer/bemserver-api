"""User groups API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import UserGroup

from bemserver_api import AutoSchema, Schema, SortField


class UserGroupSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = UserGroup

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))


class UserGroupQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
