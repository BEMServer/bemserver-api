"""Events API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Event

from bemserver_api import AutoSchema, Schema, SortField


class EventSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = Event.__table__

    id = msa.auto_field(dump_only=True)
    timestamp = ma.fields.AwareDateTime()
    campaign_scope_id = ma.fields.Int(required=True)


class EventPutSchema(EventSchema):
    class Meta(EventSchema.Meta):
        exclude = ("campaign_scope_id", "timestamp")


class EventQueryArgsSchema(Schema):
    sort = SortField(("timestamp",))
    campaign_scope_id = ma.fields.Integer()
    source = ma.fields.Str()
    category = ma.fields.Str()
    level = ma.fields.Str()
    state = ma.fields.Str()
    timestamp_min = ma.fields.AwareDateTime()
    timestamp_max = ma.fields.AwareDateTime()
