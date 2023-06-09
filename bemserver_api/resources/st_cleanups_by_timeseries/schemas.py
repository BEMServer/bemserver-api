"""ST_CleanupByTimeseries API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.scheduled_tasks import ST_CleanupByTimeseries

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields


class ST_CleanupByTimeseriesSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ST_CleanupByTimeseries

    id = msa.auto_field(dump_only=True)


class ST_CleanupByTimeseriesFullSchema(Schema):
    id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
    timeseries_name = ma.fields.Str()
    timeseries_unit_symbol = ma_fields.UnitSymbol()
    last_timestamp = ma_fields.AwareDateTime(allow_none=True)


class ST_CleanupByTimeseriesQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()


class ST_CleanupByTimeseriesFullQueryArgsSchema(Schema):
    sort = ma_fields.SortField(
        (
            "timeseries_name",
            "last_timestamp",
        )
    )
    campaign_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
    in_timeseries_name = ma.fields.Str(
        metadata={
            "description": (
                "Search for items whose name contains this input value"
                " (case insensitive)"
            ),
        }
    )
