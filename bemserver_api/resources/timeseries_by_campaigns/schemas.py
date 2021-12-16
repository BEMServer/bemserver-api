"""Timeseries by campaigns API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesByCampaign

from bemserver_api import AutoSchema


class TimeseriesByCampaignSchema(AutoSchema):
    class Meta:
        table = TimeseriesByCampaign.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesByCampaignQueryArgsSchema(ma.Schema):
    campaign_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
