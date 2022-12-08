"""Events by zones API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventByZone

from bemserver_api import AutoSchema, Schema


class EventByZoneSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EventByZone

    id = msa.auto_field(dump_only=True)


class EventByZoneQueryArgsSchema(Schema):
    zone_id = ma.fields.Int()
    event_id = ma.fields.Int()
