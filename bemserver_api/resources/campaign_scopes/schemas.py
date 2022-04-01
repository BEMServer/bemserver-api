"""Campaign scopes API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import CampaignScope

from bemserver_api import AutoSchema, Schema, SortField


class CampaignScopeSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = CampaignScope.__table__
        exclude = ("_campaign_id",)

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    campaign_id = ma.fields.Int(required=True)


class CampaignScopePutSchema(CampaignScopeSchema):
    class Meta(CampaignScopeSchema.Meta):
        exclude = CampaignScopeSchema.Meta.exclude + ("campaign_id",)


class CampaignScopeQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
