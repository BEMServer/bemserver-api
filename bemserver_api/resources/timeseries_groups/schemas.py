"""Timeseries groups API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesGroup

from bemserver_api import AutoSchema


class TimeseriesGroupSchema(AutoSchema):
    class Meta:
        table = TimeseriesGroup.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesGroupQueryArgsSchema(ma.Schema):
    name = ma.fields.Str()
