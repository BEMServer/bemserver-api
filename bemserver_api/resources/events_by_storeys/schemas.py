"""Events by storeys API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventByStorey

from bemserver_api import AutoSchema, Schema


class EventByStoreySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EventByStorey

    id = msa.auto_field(dump_only=True)


class EventByStoreyQueryArgsSchema(Schema):
    storey_id = ma.fields.Int()
    event_id = ma.fields.Int()
