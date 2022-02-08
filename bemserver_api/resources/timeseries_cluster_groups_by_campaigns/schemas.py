"""Timeseries cluster groups by campaigns API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesClusterGroupByCampaign

from bemserver_api import AutoSchema


class TimeseriesClusterGroupByCampaignSchema(AutoSchema):
    class Meta:
        table = TimeseriesClusterGroupByCampaign.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class TimeseriesClusterGroupByCampaignQueryArgsSchema(ma.Schema):
    campaign_id = ma.fields.Int()
    timeseries_cluster_group_id = ma.fields.Int()
