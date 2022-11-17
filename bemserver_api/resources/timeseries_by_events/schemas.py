"""Timeseries by events API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesByEvent

from bemserver_api import AutoSchema, Schema


class TimeseriesByEventSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesByEvent

    id = msa.auto_field(dump_only=True)


class TimeseriesByEventQueryArgsSchema(Schema):
    event_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
