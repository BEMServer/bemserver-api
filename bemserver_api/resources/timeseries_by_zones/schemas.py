"""Timeseries by zones API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesByZone

from bemserver_api import AutoSchema, Schema


class TimeseriesByZoneSchema(AutoSchema):
    class Meta:
        table = TimeseriesByZone.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesByZoneQueryArgsSchema(Schema):
    zone_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
