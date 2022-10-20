"""Zone properties API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import ZoneProperty

from bemserver_api import AutoSchema, Schema
from ..structural_element_properties.schemas import StructuralElementPropertySchema


class ZonePropertySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ZoneProperty

    id = msa.auto_field(dump_only=True)
    structural_element_property = ma.fields.Nested(
        StructuralElementPropertySchema(exclude=("id",)),
        dump_only=True,
    )


class ZonePropertyQueryArgsSchema(Schema):
    structural_element_property_id = ma.fields.Int()
