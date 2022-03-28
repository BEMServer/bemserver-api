"""Buildings API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Building

from bemserver_api import AutoSchema, Schema


class BuildingSchema(AutoSchema):
    class Meta:
        table = Building.__table__
        exclude = ("_site_id",)
        include_fk = True

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    site_id = ma.fields.Int(required=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 500))


class BuildingPutSchema(BuildingSchema):
    class Meta:
        exclude = ("site_id",)


class BuildingQueryArgsSchema(Schema):
    name = ma.fields.Str()
    site_id = ma.fields.Int()
    ifc_id = ma.fields.String()
