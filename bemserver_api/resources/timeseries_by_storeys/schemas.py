"""Timeseries by storeys API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesByStorey

from bemserver_api import AutoSchema, Schema


class TimeseriesByStoreySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesByStorey

    id = msa.auto_field(dump_only=True)


class TimeseriesByStoreyQueryArgsSchema(Schema):
    storey_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
