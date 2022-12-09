"""Events by spaces API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventBySpace

from bemserver_api import AutoSchema, Schema


class EventBySpaceSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EventBySpace

    id = msa.auto_field(dump_only=True)


class EventBySpaceQueryArgsSchema(Schema):
    space_id = ma.fields.Int()
    event_id = ma.fields.Int()
