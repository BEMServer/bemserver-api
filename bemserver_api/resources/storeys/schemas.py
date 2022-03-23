"""Storeys API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Storey

from bemserver_api import AutoSchema, Schema


class StoreySchema(AutoSchema):
    class Meta:
        table = Storey.__table__
        exclude = ("_building_id",)
        include_fk = True

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    building_id = ma.fields.Int(required=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 500))


class StoreyPutSchema(StoreySchema):
    class Meta:
        exclude = ("building_id",)


class StoreyQueryArgsSchema(Schema):
    name = ma.fields.Str()
    building_id = ma.fields.Int()
    ifc_id = ma.fields.String()
