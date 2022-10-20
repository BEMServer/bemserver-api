"""Building property data API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import BuildingPropertyData

from bemserver_api import AutoSchema, Schema


class BuildingPropertyDataSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = BuildingPropertyData

    id = msa.auto_field(dump_only=True)


class BuildingPropertyDataQueryArgsSchema(Schema):
    building_id = ma.fields.Int()
    building_property_id = ma.fields.Int()
