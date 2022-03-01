"""Timeseries groups by users API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesGroupByUser

from bemserver_api import AutoSchema


class TimeseriesGroupByUserSchema(AutoSchema):
    class Meta:
        table = TimeseriesGroupByUser.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesGroupByUserQueryArgsSchema(ma.Schema):
    user_id = ma.fields.Int()
    timeseries_group_id = ma.fields.Int()
