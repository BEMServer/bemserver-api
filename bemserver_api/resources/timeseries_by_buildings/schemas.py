"""Timeseries by buildings API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesByBuilding

from bemserver_api import AutoSchema, Schema


class TimeseriesByBuildingSchema(AutoSchema):
    class Meta:
        table = TimeseriesByBuilding.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesByBuildingQueryArgsSchema(Schema):
    building_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
