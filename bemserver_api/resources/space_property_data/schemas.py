"""Space property data API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import SpacePropertyData

from bemserver_api import AutoSchema, Schema


class SpacePropertyDataSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = SpacePropertyData

    id = msa.auto_field(dump_only=True)


class SpacePropertyDataQueryArgsSchema(Schema):
    space_id = ma.fields.Int()
    space_property_id = ma.fields.Int()
