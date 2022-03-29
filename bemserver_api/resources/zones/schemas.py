"""Zones API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Zone

from bemserver_api import AutoSchema, Schema


class ZoneSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = Zone.__table__
        exclude = ("_campaign_id",)

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    campaign_id = ma.fields.Int(required=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 500))


class ZonePutSchema(ZoneSchema):
    class Meta(ZoneSchema.Meta):
        exclude = ZoneSchema.Meta.exclude + ("campaign_id",)


class ZoneQueryArgsSchema(Schema):
    name = ma.fields.Str()
    campaign_id = ma.fields.Int()
    ifc_id = ma.fields.String()
