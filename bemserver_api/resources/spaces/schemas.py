"""Spaces API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Space

from bemserver_api import AutoSchema, Schema


class SpaceSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = Space.__table__
        exclude = ("_storey_id",)

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    storey_id = ma.fields.Int(required=True)


class SpacePutSchema(SpaceSchema):
    class Meta(SpaceSchema.Meta):
        exclude = SpaceSchema.Meta.exclude + ("storey_id",)


class SpaceQueryArgsSchema(Schema):
    name = ma.fields.Str()
    storey_id = ma.fields.Int()
    ifc_id = ma.fields.String()
