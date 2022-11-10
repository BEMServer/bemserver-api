"""Completeness API schemas"""
import marshmallow as ma

from bemserver_api import Schema
from bemserver_api.extensions.ma_fields import Timezone
from bemserver_api.resources.timeseries_data.schemas import TimeseriesBucketWidthSchema


class TimeseriesCompletenessSchema(Schema):
    name = ma.fields.String(
        metadata={
            "description": "Timeseries name",
        },
    )
    count = ma.fields.List(
        ma.fields.Integer(),
        metadata={
            "description": "Number or values for each bucket",
        },
    )
    ratio = ma.fields.List(
        ma.fields.Float(allow_none=True),
        metadata={
            "description": "Number or values / expected values for each bucket",
        },
    )
    total_count = ma.fields.Integer(
        metadata={
            "description": "Total number or values",
        },
    )
    avg_count = ma.fields.Float(
        metadata={
            "description": "Average number or values",
        },
    )
    avg_ratio = ma.fields.Float(
        allow_none=True,
        metadata={
            "description": "Average number or values / expected values",
        },
    )
    interval = ma.fields.Float(
        allow_none=True,
        metadata={
            "description": "Interval between samples (seconds), defined or inferred",
        },
    )
    undefined_interval = ma.fields.Boolean(
        metadata={
            "description": "Whether the interval was not defined",
        },
    )
    expected_count = ma.fields.List(
        ma.fields.Float(allow_none=True),
        metadata={
            "description": "Expected number or values for each bucket",
        },
    )


class CompletenessSchema(Schema):
    timestamps = ma.fields.List(
        ma.fields.AwareDateTime,
        metadata={
            "description": "Time index (value is bucket start time)",
        },
    )
    timeseries = ma.fields.Dict(
        keys=ma.fields.String(metadata={"description": "LOL"}),
        values=ma.fields.Nested(TimeseriesCompletenessSchema),
    )


class CompletenessQueryArgsSchema(TimeseriesBucketWidthSchema):
    start_time = ma.fields.AwareDateTime(
        required=True,
        metadata={
            "description": "Initial datetime",
        },
    )
    end_time = ma.fields.AwareDateTime(
        required=True,
        metadata={
            "description": "End datetime (excluded from the interval)",
        },
    )
    timeseries = ma.fields.List(
        ma.fields.Int(),
        required=True,
        metadata={
            "description": "List of timeseries ID",
        },
    )
    data_state = ma.fields.Int(
        required=True,
        metadata={
            "description": "Data state ID",
        },
    )
    timezone = Timezone(
        load_default="UTC",
        metadata={
            "description": "Timezone to use for the aggreagation",
        },
    )
