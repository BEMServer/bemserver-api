"""ST_CheckMissingByCampaign API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.scheduled_tasks import ST_CheckMissingByCampaign

from bemserver_api import AutoSchema, Schema, SortField


class ST_CheckMissingByCampaignSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ST_CheckMissingByCampaign

    id = msa.auto_field(dump_only=True)
    is_enabled = msa.auto_field(metadata={"default": True})


class ST_CheckMissingByCampaignPutSchema(Schema):
    is_enabled = ma.fields.Bool()


class ST_CheckMissingByCampaignFullSchema(Schema):
    id = ma.fields.Int()
    campaign_id = ma.fields.Int()
    campaign_name = ma.fields.Str()
    is_enabled = ma.fields.Bool()


class ST_CheckMissingByCampaignQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()


class ST_CheckMissingByCampaignFullQueryArgsSchema(Schema):
    sort = SortField(("campaign_name",))
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
