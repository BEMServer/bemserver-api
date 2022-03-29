"""Storey properties API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import StoreyProperty

from bemserver_api import AutoSchema, Schema


class StoreyPropertySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = StoreyProperty.__table__

    id = msa.auto_field(dump_only=True)


class StoreyPropertyQueryArgsSchema(Schema):
    structural_element_property_id = ma.fields.Int()
