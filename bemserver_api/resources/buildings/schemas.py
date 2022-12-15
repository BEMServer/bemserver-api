"""Buildings API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Building

from bemserver_api import AutoSchema, Schema, SortField


class BuildingSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Building

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))


class BuildingPutSchema(BuildingSchema):
    class Meta(BuildingSchema.Meta):
        exclude = ("site_id",)


class BuildingQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
    campaign_id = ma.fields.Int()
    site_id = ma.fields.Int()
    ifc_id = ma.fields.String()
