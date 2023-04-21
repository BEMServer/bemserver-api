"""Timeseries data API schemas"""
import marshmallow as ma

from bemserver_core.input_output.timeseries_data_io import AGGREGATION_FUNCTIONS
from bemserver_core.time_utils import PERIODS, FIXED_SIZE_PERIODS

from bemserver_api import Schema
from bemserver_api.extensions import ma_fields


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


class TimeseriesDataGetStatsBaseQueryArgsSchema(Schema):
    data_state = ma.fields.Int(
        required=True,
        metadata={
            "description": "Data state ID",
        },
    )
    timezone = ma_fields.Timezone(
        load_default="UTC",
        metadata={
            "description": "Timezone to use for response data",
        },
    )


class TimeseriesDataGetStatsByIDBaseQueryArgsSchema(
    TimeseriesIDListMixinSchema, TimeseriesDataGetStatsBaseQueryArgsSchema
):
    """Timeseries stats by ID query parameters"""


class TimeseriesDataGetStatsByNameBaseQueryArgsSchema(
    TimeseriesNameListMixinSchema, TimeseriesDataGetStatsBaseQueryArgsSchema
):
    """Timeseries stats by name query parameters"""


class TSStatsSchema(Schema):
    first_timestamp = ma_fields.AwareDateTime(
        metadata={
            "description": "First datetime",
        },
    )
    last_timestamp = ma_fields.AwareDateTime(
        metadata={
            "description": "Last datetime",
        },
    )
    count = ma.fields.Integer(
        metadata={
            "description": "Values count",
        },
    )
    min = ma.fields.Float(
        metadata={
            "description": "Minimum value",
        },
    )
    max = ma.fields.Float(
        metadata={
            "description": "Maximum value",
        },
    )
    avg = ma.fields.Float(
        metadata={
            "description": "Minimum value",
        },
    )
    stddev = ma.fields.Float(
        metadata={
            "description": "Standard deviation",
        },
    )


class TimeseriesDataStatsByIDSchema(Schema):
    """Timeseries stats response schema"""

    stats = ma.fields.Dict(
        keys=ma.fields.Integer(),
        values=ma.fields.Nested(TSStatsSchema()),
    )


class TimeseriesDataStatsByNameSchema(Schema):
    """Timeseries stats response schema"""

    stats = ma.fields.Dict(
        keys=ma.fields.String(),
        values=ma.fields.Nested(TSStatsSchema()),
    )


class TimeseriesDataBaseQueryArgsSchema(Schema):
    """Timeseries values query parameters base schema"""

    start_time = ma_fields.AwareDateTime(
        required=True,
        metadata={
            "description": "Initial datetime",
        },
    )
    end_time = ma_fields.AwareDateTime(
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

    timezone = ma_fields.Timezone(
        load_default="UTC",
        metadata={
            "description": "Timezone to use for response data",
        },
    )

    convert_to = ma.fields.List(
        ma_fields.UnitSymbol(),
        metadata={
            "description": (
                "Optional list of units to convert to. "
                "If passed, must be of same length as timeseries list. "
                "Empty string means no conversion for a timeseries."
            ),
        },
    )

    @ma.validates_schema
    def validate_convert_to(self, data, **kwargs):
        if "convert_to" in data and (
            len(data["convert_to"]) != len(data["timeseries"])
        ):
            raise ma.ValidationError(
                "If provided, convert_to must be the same size as timeseries."
            )

    @ma.post_load
    def make_convert_to_mapping(self, data, **kwargs):
        if "convert_to" in data:
            data["convert_to"] = {
                ts_label: unit
                for ts_label, unit in zip(data["timeseries"], data["convert_to"])
                if unit
            }
        return data


class TimeseriesDataGetByIDQueryArgsSchema(
    TimeseriesDataGetBaseQueryArgsSchema, TimeseriesIDListMixinSchema
):
    """Timeseries values GET by ID query parameters schema"""


class TimeseriesDataGetByNameQueryArgsSchema(
    TimeseriesDataGetBaseQueryArgsSchema, TimeseriesNameListMixinSchema
):
    """Timeseries values GET by name query parameters schema"""


class TimeseriesBucketWidthSchema(Schema):
    """Timeseries bucket width schema, with custom validation on fixed size periods"""

    _VALIDATION_MSG = (
        f"Only fixed bucket width units ({', '.join(FIXED_SIZE_PERIODS)})"
        " accept a value different than 1."
    )

    bucket_width_value = ma.fields.Int(
        validate=ma.validate.Range(min=1),
        required=True,
        metadata={
            "description": _VALIDATION_MSG,
        },
    )
    bucket_width_unit = ma.fields.String(
        validate=ma.validate.OneOf(PERIODS),
        required=True,
    )

    @ma.validates_schema
    def validate_bucket(self, data, **kwargs):
        if (
            data["bucket_width_unit"] not in FIXED_SIZE_PERIODS
            and data["bucket_width_value"] != 1
        ):
            raise ma.ValidationError(
                self._VALIDATION_MSG,
                field_name="bucket_width_value",
                data=data["bucket_width_value"],
                valid_data=FIXED_SIZE_PERIODS,
            )


class TimeseriesDataGetAggregateBaseQueryArgsSchema(
    TimeseriesDataGetBaseQueryArgsSchema,
    TimeseriesBucketWidthSchema,
):
    """Timeseries values aggregate GET query parameters base schema"""

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
