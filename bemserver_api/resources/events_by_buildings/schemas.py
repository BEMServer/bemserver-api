"""Events by buildings API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventByBuilding

from bemserver_api import AutoSchema, Schema


class EventByBuildingSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EventByBuilding

    id = msa.auto_field(dump_only=True)


class EventByBuildingQueryArgsSchema(Schema):
    building_id = ma.fields.Int()
    event_id = ma.fields.Int()
