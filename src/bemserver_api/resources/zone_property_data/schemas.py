"""Zone property data API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import ZonePropertyData

from bemserver_api import AutoSchema, Schema

from ..zone_properties.schemas import ZonePropertySchema


class ZonePropertyDataSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ZonePropertyData

    id = msa.auto_field(dump_only=True)
    zone_property = ma.fields.Nested(
        ZonePropertySchema(exclude=("id",)),
        dump_only=True,
    )


class ZonePropertyDataQueryArgsSchema(Schema):
    zone_id = ma.fields.Int()
    zone_property_id = ma.fields.Int()
