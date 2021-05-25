"""Timeseries by campaigns API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesByCampaign

from bemserver_api import Schema, AutoSchema


class TimeseriesByCampaignSchema(AutoSchema):
    class Meta:
        table = TimeseriesByCampaign.__table__

    id = msa.auto_field(dump_only=True)
    campaign_id = msa.auto_field()
    timeseries_id = msa.auto_field()


class TimeseriesByCampaignQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
