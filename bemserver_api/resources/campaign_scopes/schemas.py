"""Campaign scopes API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import CampaignScope

from bemserver_api import AutoSchema, Schema


class CampaignScopeSchema(AutoSchema):
    class Meta:
        table = CampaignScope.__table__

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    description = msa.auto_field(validate=ma.validate.Length(1, 500))
    campaign_id = ma.fields.Int(required=True)


class CampaignScopePutSchema(CampaignScopeSchema):
    class Meta:
        exclude = ("campaign_id",)


class CampaignScopeQueryArgsSchema(Schema):
    name = ma.fields.Str()
