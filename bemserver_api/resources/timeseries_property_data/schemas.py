"""Timeseries property data"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesPropertyData

from bemserver_api import AutoSchema, Schema


class TimeseriesPropertyDataSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesPropertyData

    id = msa.auto_field(dump_only=True)


class TimeseriesPropertyDataQueryArgsSchema(Schema):
    timeseries_id = ma.fields.Int()
    property_id = ma.fields.Int()
