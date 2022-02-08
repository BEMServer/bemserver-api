"""Timeseries cluster groups API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesClusterGroup

from bemserver_api import AutoSchema


class TimeseriesClusterGroupSchema(AutoSchema):
    class Meta:
        table = TimeseriesClusterGroup.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesClusterGroupQueryArgsSchema(ma.Schema):
    name = ma.fields.Str()
