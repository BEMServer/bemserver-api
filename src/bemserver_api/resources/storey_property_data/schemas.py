"""Storey property data API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import StoreyPropertyData

from bemserver_api import AutoSchema, Schema

from ..storey_properties.schemas import StoreyPropertySchema


class StoreyPropertyDataSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = StoreyPropertyData

    id = msa.auto_field(dump_only=True)
    storey_property = ma.fields.Nested(
        StoreyPropertySchema(exclude=("id",)),
        dump_only=True,
    )


class StoreyPropertyDataQueryArgsSchema(Schema):
    storey_id = ma.fields.Int()
    storey_property_id = ma.fields.Int()
