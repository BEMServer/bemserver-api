"""Users by campaigns API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import UserByCampaign

from bemserver_api import AutoSchema


class UserByCampaignSchema(AutoSchema):
    class Meta:
        table = UserByCampaign.__table__

    id = msa.auto_field(dump_only=True)
    campaign_id = msa.auto_field()
    user_id = msa.auto_field()


class UserByCampaignQueryArgsSchema(ma.Schema):
    campaign_id = ma.fields.Int()
    user_id = ma.fields.Int()
