"""Events API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Event, EventLevelEnum

from bemserver_api import AutoSchema, Schema, SortField


class EventSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Event

    id = msa.auto_field(dump_only=True)
    timestamp = ma.fields.AwareDateTime()
    level = ma.fields.Enum(EventLevelEnum)


class EventPutSchema(EventSchema):
    class Meta(EventSchema.Meta):
        exclude = ("campaign_scope_id", "timestamp")


class EventQueryArgsSchema(Schema):
    sort = SortField(("timestamp", "level"))
    campaign_id = ma.fields.Integer()
    campaign_scope_id = ma.fields.Integer()
    user_id = ma.fields.Integer()
    source = ma.fields.String()
    in_source = ma.fields.String()
    category_id = ma.fields.Int()
    level = ma.fields.Enum(EventLevelEnum)
    level_min = ma.fields.Enum(EventLevelEnum)
    timestamp_min = ma.fields.AwareDateTime()
    timestamp_max = ma.fields.AwareDateTime()
    timeseries_id = ma.fields.Integer()


class EventRecurseArgsSchema(Schema):
    recurse = ma.fields.Boolean()
