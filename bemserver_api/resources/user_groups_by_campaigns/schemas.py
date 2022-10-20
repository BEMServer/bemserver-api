"""User groups by campaigns API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import UserGroupByCampaign

from bemserver_api import AutoSchema, Schema


class UserGroupByCampaignSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = UserGroupByCampaign

    id = msa.auto_field(dump_only=True)


class UserGroupByCampaignQueryArgsSchema(Schema):
    user_group_id = ma.fields.Int()
    campaign_id = ma.fields.Int()
