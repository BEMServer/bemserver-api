"""Timeseries clusters API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesCluster

from bemserver_api import AutoSchema


class TimeseriesClusterSchema(AutoSchema):
    class Meta:
        table = TimeseriesCluster.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    description = msa.auto_field(validate=ma.validate.Length(1, 500))
    unit_symbol = msa.auto_field(validate=ma.validate.Length(1, 20))


class TimeseriesClusterQueryArgsSchema(ma.Schema):
    name = ma.fields.Str()
    unit_symbol = ma.fields.Str()
    campaign_id = ma.fields.Int()
    user_id = ma.fields.Int()
