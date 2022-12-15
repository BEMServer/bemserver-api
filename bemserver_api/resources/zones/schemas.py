"""Zones API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Zone

from bemserver_api import AutoSchema, Schema, SortField


class ZoneSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Zone

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))


class ZonePutSchema(ZoneSchema):
    class Meta(ZoneSchema.Meta):
        exclude = ("campaign_id",)


class ZoneQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
    campaign_id = ma.fields.Int()
    ifc_id = ma.fields.String()
