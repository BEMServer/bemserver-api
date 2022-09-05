"""ST_CleanupByTimeseries API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.scheduled_tasks import ST_CleanupByTimeseries

from bemserver_api import AutoSchema, Schema


class ST_CleanupByTimeseriesSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = ST_CleanupByTimeseries.__table__

    id = msa.auto_field(dump_only=True)


class ST_CleanupByTimeseriesQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
