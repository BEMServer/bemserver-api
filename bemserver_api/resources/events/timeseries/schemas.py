"""TimeseriesEvents API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesEvent

from bemserver_api import AutoSchema


class TimeseriesEventSchema(AutoSchema):
    class Meta:
        table = TimeseriesEvent.__table__
        exclude = ("_channel_id", "_timestamp")
        include_fk = True

    id = msa.auto_field(dump_only=True)
    channel_id = ma.fields.Integer()
    timestamp = ma.fields.AwareDateTime()


class TimeseriesEventPutSchema(TimeseriesEventSchema):
    class Meta:
        exclude = ("channel_id", "timestamp")


class TimeseriesEventQueryArgsSchema(ma.Schema):
    channel_id = ma.fields.Integer()
    source = ma.fields.Str()
    category = ma.fields.Str()
    level = ma.fields.Str()
    state = ma.fields.Str()
    # TODO: timestamp min/max
    timestamp = ma.fields.AwareDateTime()
