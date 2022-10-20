"""User groups by campaign scopes API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import UserGroupByCampaignScope

from bemserver_api import AutoSchema, Schema


class UserGroupByCampaignScopeSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = UserGroupByCampaignScope

    id = msa.auto_field(dump_only=True)


class UserGroupByCampaignScopeQueryArgsSchema(Schema):
    user_group_id = ma.fields.Int()
    campaign_scope_id = ma.fields.Int()
