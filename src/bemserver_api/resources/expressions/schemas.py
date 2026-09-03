"""Expressions API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.common import AggregationFunctionsEnum
from bemserver_core.model import Expression, ExpressionVariable

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields
from bemserver_api.resources.timeseries_data.schemas import TimeseriesBucketWidthSchema


class ExpressionVariableSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ExpressionVariable
        exclude = ("id", "campaign_scope_id", "expression_id")

    aggregation = ma.fields.Enum(
        AggregationFunctionsEnum,
        by_value=True,
        load_default=AggregationFunctionsEnum.AVG,
    )


class ExpressionSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Expression

    id = msa.auto_field(dump_only=True)
    variables = ma.fields.List(
        ma.fields.Nested(ExpressionVariableSchema), required=True
    )

    @ma.pre_dump
    def to_dict(self, data, many, **kwargs):
        return data.to_dict()


class ExpressionPutSchema(ExpressionSchema):
    class Meta(ExpressionSchema.Meta):
        exclude = ("campaign_scope_id",)


class ExpressionQueryArgsSchema(Schema):
    sort = ma_fields.SortField(("id",))
    campaign_scope_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()


class ExpressionEvaluateSchema(ExpressionSchema):
    class Meta(ExpressionSchema):
        exclude = ("campaign_scope_id",)


class ExpressionEvaluateQueryArgsSchema(TimeseriesBucketWidthSchema):
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
    timezone = ma_fields.Timezone(
        load_default="UTC",
        metadata={
            "description": "Timezone to use for aggregation",
        },
    )
