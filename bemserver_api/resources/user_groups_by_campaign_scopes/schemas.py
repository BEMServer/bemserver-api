"""User groups by campaign scopes API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import UserGroupByCampaignScope

from bemserver_api import AutoSchema


class UserGroupByCampaignScopeSchema(AutoSchema):
    class Meta:
        table = UserGroupByCampaignScope.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class UserGroupByCampaignScopeQueryArgsSchema(ma.Schema):
    user_group_id = ma.fields.Int()
    campaign_scope_id = ma.fields.Int()