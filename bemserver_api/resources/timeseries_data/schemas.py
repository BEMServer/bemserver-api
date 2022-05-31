"""Timeseries data API schemas"""
import marshmallow as ma
from flask_smorest.fields import Upload

from bemserver_core.input_output.timeseries_data_io import AGGREGATION_FUNCTIONS

from bemserver_api import Schema
from bemserver_api.extensions.ma_fields import Timezone


class TimeseriesIDListMixinSchema(Schema):
    timeseries = ma.fields.List(
        ma.fields.Int(),
        required=True,
        metadata={
            "description": "List of timeseries ID",
        },
    )


class TimeseriesNameListMixinSchema(Schema):
    timeseries = ma.fields.List(
        ma.fields.String(),
        required=True,
        metadata={
            "description": "List of timeseries names",
        },
    )


class TimeseriesDataGetBaseQueryArgsSchema(Schema):
    """Timeseries values GET query parameters base schema"""

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
    data_state = ma.fields.Int(
        required=True,
        metadata={
            "description": "Data state ID",
        },
    )


class TimeseriesDataGetByIDQueryArgsSchema(
    TimeseriesDataGetBaseQueryArgsSchema, TimeseriesIDListMixinSchema
):
    """Timeseries values GET by ID query parameters schema"""


class TimeseriesDataGetByNameQueryArgsSchema(
    TimeseriesDataGetBaseQueryArgsSchema, TimeseriesNameListMixinSchema
):
    """Timeseries values GET by name query parameters schema"""


class TimeseriesDataGetAggregateBaseQueryArgsSchema(
    TimeseriesDataGetBaseQueryArgsSchema
):
    """Timeseries values aggregate GET query parameters base schema"""

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


class TimeseriesDataGetByIDAggregateQueryArgsSchema(
    TimeseriesDataGetAggregateBaseQueryArgsSchema, TimeseriesIDListMixinSchema
):
    """Timeseries values aggregate GET by ID query parameters schema"""


class TimeseriesDataGetByNameAggregateQueryArgsSchema(
    TimeseriesDataGetAggregateBaseQueryArgsSchema, TimeseriesNameListMixinSchema
):
    """Timeseries values aggregate GET by name query parameters schema"""


class TimeseriesDataPostQueryArgsSchema(Schema):
    """Timeseries values POST query parameters schema"""

    data_state = ma.fields.Int(
        required=True,
        metadata={
            "description": "Data state ID",
        },
    )


class TimeseriesDataPostFileSchema(Schema):
    csv_file = Upload(
        required=True,
    )
