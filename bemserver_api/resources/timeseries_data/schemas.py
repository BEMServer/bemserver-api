"""Timeseries data API schemas"""
import marshmallow as ma
from flask_smorest.fields import Upload

from bemserver_core.input_output.timeseries_data_io import (
    AGGREGATION_FUNCTIONS,
    INTERVAL_UNITS,
)

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


class TimeseriesDataBaseQueryArgsSchema(Schema):
    """Timeseries values query parameters base schema"""

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


class TimeseriesDataDeleteByIDQueryArgsSchema(
    TimeseriesDataBaseQueryArgsSchema, TimeseriesIDListMixinSchema
):
    """Timeseries values DELETE by ID query parameters schema"""


class TimeseriesDataDeleteByNameQueryArgsSchema(
    TimeseriesDataBaseQueryArgsSchema, TimeseriesNameListMixinSchema
):
    """Timeseries values DELETE by name query parameters schema"""


class TimeseriesDataGetBaseQueryArgsSchema(TimeseriesDataBaseQueryArgsSchema):
    """Timeseries values GET query parameters base schema"""

    timezone = Timezone(
        load_default="UTC",
        metadata={
            "description": "Timezone to use for response data",
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

    bucket_width_value = ma.fields.Int(
        validate=ma.validate.Range(min=1),
        required=True,
    )
    bucket_width_unit = ma.fields.String(
        validate=ma.validate.OneOf(INTERVAL_UNITS),
        required=True,
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
