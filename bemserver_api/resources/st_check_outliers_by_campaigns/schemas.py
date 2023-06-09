"""ST_CheckOutliersByCampaign API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.scheduled_tasks import ST_CheckOutliersByCampaign

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields


class ST_CheckOutliersByCampaignSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ST_CheckOutliersByCampaign

    id = msa.auto_field(dump_only=True)
    is_enabled = msa.auto_field(metadata={"default": True})


class ST_CheckOutliersByCampaignPutSchema(Schema):
    is_enabled = ma.fields.Bool()


class ST_CheckOutliersByCampaignFullSchema(Schema):
    id = ma.fields.Int()
    campaign_id = ma.fields.Int()
    campaign_name = ma.fields.Str()
    is_enabled = ma.fields.Bool()


class ST_CheckOutliersByCampaignQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()


class ST_CheckOutliersByCampaignFullQueryArgsSchema(Schema):
    sort = ma_fields.SortField(("campaign_name",))
    is_enabled = ma.fields.Bool()
    campaign_id = ma.fields.Int()
    in_campaign_name = ma.fields.Str(
        metadata={
            "description": (
                "Search for items whose name contains this input value"
                " (case insensitive)"
            ),
        }
    )
