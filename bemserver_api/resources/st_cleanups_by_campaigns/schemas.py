"""ST_CleanupByCampaign API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.scheduled_tasks import ST_CleanupByCampaign

from bemserver_api import AutoSchema, Schema


class ST_CleanupByCampaignSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = ST_CleanupByCampaign.__table__

    id = msa.auto_field(dump_only=True)


class ST_CleanupByCampaignQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
