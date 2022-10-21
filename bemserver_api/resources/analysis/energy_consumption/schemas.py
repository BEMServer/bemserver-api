"""Energy consumption API schemas"""
import marshmallow as ma

from bemserver_core.input_output.timeseries_data_io import INTERVAL_UNITS

from bemserver_api import Schema
from bemserver_api.extensions.ma_fields import Timezone


class EnergyConsumptionSchema(Schema):
    timestamps = ma.fields.List(
        ma.fields.AwareDateTime,
        metadata={
            "description": "Time index (value is bucket start time)",
        },
    )
    energy = ma.fields.Dict(
        keys=ma.fields.String(metadata={"description": "Energy"}),
        values=ma.fields.Dict(
            keys=ma.fields.String(metadata={"description": "End use"}),
            values=ma.fields.List(
                ma.fields.Float(metadata={"description": "Value (Wh)"})
            ),
        ),
    )


class EnergyConsumptionQueryArgsSchema(Schema):
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
    bucket_width_value = ma.fields.Int(
        validate=ma.validate.Range(min=1),
        required=True,
    )
    bucket_width_unit = ma.fields.String(
        validate=ma.validate.OneOf(INTERVAL_UNITS),
        required=True,
    )
    timezone = Timezone(
        load_default="UTC",
        metadata={
            "description": "Timezone to use for the aggreagation",
        },
    )
