"""Timeseries groups by campaigns API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesGroupByCampaign

from bemserver_api import AutoSchema


class TimeseriesGroupByCampaignSchema(AutoSchema):
    class Meta:
        table = TimeseriesGroupByCampaign.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesGroupByCampaignQueryArgsSchema(ma.Schema):
    campaign_id = ma.fields.Int()
    timeseries_group_id = ma.fields.Int()
