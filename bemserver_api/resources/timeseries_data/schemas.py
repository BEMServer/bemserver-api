"""Timeseries data API schemas"""
import marshmallow as ma
from flask_smorest.fields import Upload

from bemserver_core.csv_io import AGGREGATION_FUNCTIONS

from bemserver_api.extensions.ma_fields import Timezone


class TimeseriesDataGetQueryArgsSchema(ma.Schema):
    """Timeseries values GET query parameters schema"""

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


class TimeseriesDataGetAggregateQueryArgsSchema(TimeseriesDataGetQueryArgsSchema):
    """Timeseries values aggregate GET query parameters schema"""

    # TODO: Create custom field for bucket width
    bucket_width = ma.fields.String(
        required=True,
        metadata={
            "description": "Bucket width (ISO 8601 duration or PostgreSQL)",
        },
    )
    timezone = Timezone(
        load_default="UTC",
        metadata={
            "description": "Timezone to use for the aggreagation",
        },
    )
    aggregation = ma.fields.String(
        load_default="avg",
        validate=ma.validate.OneOf(AGGREGATION_FUNCTIONS),
    )


class TimeseriesDataPostQueryArgsSchema(ma.Schema):
    """Timeseries values POST query parameters schema"""

    data_state = ma.fields.Int(
        required=True,
        metadata={
            "description": "Data state ID",
        },
    )


class TimeseriesDataPostFileSchema(ma.Schema):
    csv_file = Upload()
