"""Timeseries cluster property data"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesClusterPropertyData

from bemserver_api import AutoSchema


class TimeseriesClusterPropertyDataSchema(AutoSchema):
    class Meta:
        table = TimeseriesClusterPropertyData.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesClusterPropertyDataQueryArgsSchema(ma.Schema):
    cluster_id = ma.fields.Int()
    property_id = ma.fields.Int()
