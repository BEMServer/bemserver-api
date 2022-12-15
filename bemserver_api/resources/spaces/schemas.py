"""Spaces API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Space

from bemserver_api import AutoSchema, Schema, SortField


class SpaceSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Space

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))


class SpacePutSchema(SpaceSchema):
    class Meta(SpaceSchema.Meta):
        exclude = ("storey_id",)


class SpaceQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
    campaign_id = ma.fields.Int()
    site_id = ma.fields.Int()
    building_id = ma.fields.Int()
    storey_id = ma.fields.Int()
    ifc_id = ma.fields.String()
