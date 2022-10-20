"""Timeseries by spaces API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesBySpace

from bemserver_api import AutoSchema, Schema


class TimeseriesBySpaceSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesBySpace

    id = msa.auto_field(dump_only=True)


class TimeseriesBySpaceQueryArgsSchema(Schema):
    space_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
