"""API"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from ...model import TestPluginEnableCampaign

from bemserver_api import AutoSchema, Schema


class TestPluginEnableCampaignSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = TestPluginEnableCampaign.__table__

    id = msa.auto_field(dump_only=True)


class TestPluginEnableCampaignQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
    enabled = ma.fields.Boolean()
