"""Sites API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Site

from bemserver_api import AutoSchema, Schema
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
    sort = ma_fields.SortField(("name",))
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


class GetDegreeDaysQueryArgsSchema(Schema):
    start_date = ma.fields.Date(
        required=True,
        metadata={
            "description": "Initial date",
        },
    )
    end_date = ma.fields.Date(
        required=True,
        metadata={
            "description": "End date (excluded from the interval)",
        },
    )
    period = ma.fields.String(validate=ma.validate.OneOf(("day", "month", "year")))
    type_ = ma.fields.String(
        data_key="type",
        validate=ma.validate.OneOf(("heating", "cooling")),
        load_default="heating",
    )
    base = ma.fields.Float(load_default=18.0)
    unit = ma_fields.UnitSymbol(load_default="°C")


class DegreeDaysSchema(Schema):
    """Degree days response schema"""

    degree_days = ma.fields.Dict(
        keys=ma_fields.AwareDateTime(),
        values=ma.fields.Float(),
    )
