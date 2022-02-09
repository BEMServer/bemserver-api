"""Timeseries cluster groups by users API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesClusterGroupByUser

from bemserver_api import AutoSchema


class TimeseriesClusterGroupByUserSchema(AutoSchema):
    class Meta:
        table = TimeseriesClusterGroupByUser.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesClusterGroupByUserQueryArgsSchema(ma.Schema):
    user_id = ma.fields.Int()
    timeseries_cluster_group_id = ma.fields.Int()
