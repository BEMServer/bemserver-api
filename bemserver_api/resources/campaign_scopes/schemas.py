"""Campaign scopes API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import CampaignScope

from bemserver_api import AutoSchema, Schema, SortField


class CampaignScopeSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = CampaignScope

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))


class CampaignScopePutSchema(CampaignScopeSchema):
    class Meta(CampaignScopeSchema.Meta):
        exclude = ("campaign_id",)


class CampaignScopeQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
    campaign_id = ma.fields.Int()
