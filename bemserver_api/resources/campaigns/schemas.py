"""Campaigns API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Campaign

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields


class CampaignSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Campaign

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    start_time = ma_fields.AwareDateTime()
    end_time = ma_fields.AwareDateTime()
    timezone = ma_fields.Timezone(
        required=True,
        metadata={
            "default": "UTC",
            "description": "Timezone used to localize timeseries in this campaign",
        },
    )


class CampaignQueryArgsSchema(Schema):
    sort = ma_fields.SortField(("name",))
    name = ma.fields.Str()
    in_name = ma.fields.Str(
        metadata={
            "description": (
                "Search for items whose name contains this input value"
                " (case insensitive)"
            ),
        }
    )
