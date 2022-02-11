"""Timeseries properties API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesProperty

from bemserver_api import AutoSchema


class TimeseriesPropertySchema(AutoSchema):
    class Meta:
        table = TimeseriesProperty.__table__

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    description = msa.auto_field(validate=ma.validate.Length(1, 250))
