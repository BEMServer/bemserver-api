"""Energy consumption API schemas"""
import marshmallow as ma

from bemserver_api import Schema
from bemserver_api.extensions.ma_fields import Timezone
from bemserver_api.resources.timeseries_data.schemas import TimeseriesBucketWidthSchema


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


class EnergyConsumptionQueryArgsSchema(TimeseriesBucketWidthSchema):
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
    timezone = Timezone(
        load_default="UTC",
        metadata={
            "description": "Timezone to use for the aggreagation",
        },
    )
