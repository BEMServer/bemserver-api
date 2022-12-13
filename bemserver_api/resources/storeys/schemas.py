"""Storeys API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Storey

from bemserver_api import AutoSchema, Schema, SortField


class StoreySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Storey

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))


class StoreyPutSchema(StoreySchema):
    class Meta(StoreySchema.Meta):
        exclude = ("building_id",)


class StoreyQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
    campaign_id = ma.fields.Int()
    site_id = ma.fields.Int()
    building_id = ma.fields.Int()
    ifc_id = ma.fields.String()
