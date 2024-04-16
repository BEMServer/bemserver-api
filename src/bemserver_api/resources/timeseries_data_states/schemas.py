"""Timeseries data states API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesDataState

from bemserver_api import AutoSchema


class TimeseriesDataStateSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesDataState

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
