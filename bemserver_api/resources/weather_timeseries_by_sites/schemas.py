"""Weather timeseries by sites API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import WeatherParameterEnum, WeatherTimeseriesBySite

from bemserver_api import AutoSchema, Schema
from ..timeseries.schemas import TimeseriesSchema


class WeatherTimeseriesBySiteSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = WeatherTimeseriesBySite

    id = msa.auto_field(dump_only=True)
    parameter = ma.fields.Enum(WeatherParameterEnum)
    timeseries = ma.fields.Nested(TimeseriesSchema(exclude=("id",)), dump_only=True)


class WeatherTimeseriesBySiteQueryArgsSchema(Schema):
    site_id = ma.fields.Int()
    parameter = ma.fields.String()
    timeseries_id = ma.fields.Int()
    forecast = ma.fields.Boolean()
