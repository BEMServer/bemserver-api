"""Weather timeseries by sites API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import WeatherParameterEnum, WeatherTimeseriesBySite

from bemserver_api import AutoSchema, Schema


class WeatherTimeseriesBySiteSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = WeatherTimeseriesBySite

    id = msa.auto_field(dump_only=True)
    parameter = ma.fields.Enum(WeatherParameterEnum)


class WeatherTimeseriesBySiteQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
    site_id = ma.fields.Int()
    parameter = ma.fields.String()
    timeseries_id = ma.fields.Int()
