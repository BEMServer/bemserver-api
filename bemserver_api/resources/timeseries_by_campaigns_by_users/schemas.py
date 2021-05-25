"""Timeseries by campaigns by users API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesByCampaignByUser

from bemserver_api import Schema, AutoSchema


class TimeseriesByCampaignByUserSchema(AutoSchema):
    class Meta:
        table = TimeseriesByCampaignByUser.__table__

    id = msa.auto_field(dump_only=True)
    user_id = msa.auto_field()
    timeseries_by_campaign_id = msa.auto_field()


class TimeseriesByCampaignByUserQueryArgsSchema(Schema):
    user_id = ma.fields.Int()
    timeseries_by_campaign_id = ma.fields.Int()
