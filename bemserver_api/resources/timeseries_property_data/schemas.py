"""Timeseries property data"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesPropertyData

from bemserver_api import AutoSchema


class TimeseriesPropertyDataSchema(AutoSchema):
    class Meta:
        table = TimeseriesPropertyData.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesPropertyDataQueryArgsSchema(ma.Schema):
    timeseries_id = ma.fields.Int()
    property_id = ma.fields.Int()
