"""ST_DownloadWeatherForecastDataBySite API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.scheduled_tasks import ST_DownloadWeatherForecastDataBySite

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields


class ST_DownloadWeatherForecastDataBySiteSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ST_DownloadWeatherForecastDataBySite

    id = msa.auto_field(dump_only=True)
    is_enabled = msa.auto_field(metadata={"default": True})


class ST_DownloadWeatherForecastDataBySitePutSchema(
    ST_DownloadWeatherForecastDataBySiteSchema
):
    class Meta(ST_DownloadWeatherForecastDataBySiteSchema.Meta):
        exclude = ("site_id",)


class ST_DownloadWeatherForecastDataBySiteFullSchema(Schema):
    id = ma.fields.Int()
    site_id = ma.fields.Int()
    site_name = ma.fields.Str()
    is_enabled = ma.fields.Bool()


class ST_DownloadWeatherForecastDataBySiteQueryArgsSchema(Schema):
    site_id = ma.fields.Int()


class ST_DownloadWeatherForecastDataBySiteFullQueryArgsSchema(Schema):
    sort = ma_fields.SortField(
        (
            "campaign_id",
            "site_name",
        )
    )
    is_enabled = ma.fields.Bool()
    campaign_id = ma.fields.Int()
    site_id = ma.fields.Int()
    in_site_name = ma.fields.Str(
        metadata={
            "description": (
                "Search for items whose name contains this input value"
                " (case insensitive)"
            ),
        }
    )
