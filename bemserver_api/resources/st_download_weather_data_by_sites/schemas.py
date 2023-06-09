"""ST_DownloadWeatherDataBySite API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.scheduled_tasks import ST_DownloadWeatherDataBySite

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields


class ST_DownloadWeatherDataBySiteSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ST_DownloadWeatherDataBySite

    id = msa.auto_field(dump_only=True)
    is_enabled = msa.auto_field(metadata={"default": True})


class ST_DownloadWeatherDataBySitePutSchema(ST_DownloadWeatherDataBySiteSchema):
    class Meta(ST_DownloadWeatherDataBySiteSchema.Meta):
        exclude = ("site_id",)


class ST_DownloadWeatherDataBySiteFullSchema(Schema):
    id = ma.fields.Int()
    site_id = ma.fields.Int()
    site_name = ma.fields.Str()
    is_enabled = ma.fields.Bool()


class ST_DownloadWeatherDataBySiteQueryArgsSchema(Schema):
    site_id = ma.fields.Int()


class ST_DownloadWeatherDataBySiteFullQueryArgsSchema(Schema):
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
