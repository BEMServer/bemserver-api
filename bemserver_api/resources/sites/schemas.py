"""Sites API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Site

from bemserver_api import AutoSchema, Schema, SortField
from bemserver_api.extensions import ma_fields


class SiteSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Site

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    latitude = msa.auto_field(validate=ma.validate.Range(-90, 90))
    longitude = msa.auto_field(validate=ma.validate.Range(-180, 180))


class SitePutSchema(SiteSchema):
    class Meta(SiteSchema.Meta):
        exclude = ("campaign_id",)


class SiteQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
    campaign_id = ma.fields.Int()
    ifc_id = ma.fields.String()


class DownloadWeatherDataQueryArgsSchema(Schema):
    start_time = ma_fields.AwareDateTime(
        required=True,
        metadata={
            "description": "Initial datetime",
        },
    )
    end_time = ma_fields.AwareDateTime(
        required=True,
        metadata={
            "description": "End datetime (excluded from the interval)",
        },
    )
