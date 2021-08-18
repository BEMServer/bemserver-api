"""Campaigns API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Campaign

from bemserver_api import AutoSchema


class CampaignSchema(AutoSchema):
    class Meta:
        table = Campaign.__table__

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    description = msa.auto_field(validate=ma.validate.Length(1, 500))
    start_time = ma.fields.AwareDateTime()
    end_time = ma.fields.AwareDateTime()


class CampaignQueryArgsSchema(ma.Schema):
    name = ma.fields.Str()
