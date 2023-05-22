"""Energy consumption API schemas"""
import marshmallow as ma

from bemserver_api import Schema
from bemserver_api.extensions import ma_fields
from bemserver_api.resources.timeseries_data.schemas import TimeseriesBucketWidthSchema


class EnergyConsumptionSchema(Schema):
    timestamps = ma.fields.List(
        ma_fields.AwareDateTime,
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


class EnergyConsumptionQueryArgsSchema(TimeseriesBucketWidthSchema):
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
    timezone = ma_fields.Timezone(
        load_default="UTC",
        metadata={
            "description": "Timezone to use for the aggreagation",
        },
    )
    unit = ma_fields.UnitSymbol(load_default="Wh")
    ratio_property = ma.fields.String()
