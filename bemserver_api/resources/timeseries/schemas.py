"""Timeseries API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Timeseries

from bemserver_api import AutoSchema


class TimeseriesSchema(AutoSchema):
    class Meta:
        table = Timeseries.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesQueryArgsSchema(ma.Schema):
    name = ma.fields.Str()
    cluster_id = ma.fields.Int()
    data_state_id = ma.fields.Int()
