"""Expressions API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.common import AggregationFunctionsEnum
from bemserver_core.model import Expression, ExpressionVariable

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields


class ExpressionSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Expression

    id = msa.auto_field(dump_only=True)


class ExpressionPutSchema(ExpressionSchema):
    class Meta(ExpressionSchema.Meta):
        exclude = ("campaign_scope_id",)


class ExpressionQueryArgsSchema(Schema):
    sort = ma_fields.SortField(("id",))
    campaign_scope_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()


class ExpressionVariableSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ExpressionVariable
        exclude = ("id", "campaign_scope_id", "expression_id")

    aggregation = ma.fields.Enum(
        AggregationFunctionsEnum,
        by_value=True,
    )


class ExpressionFullSchema(ExpressionSchema):
    variables = ma.fields.List(
        ma.fields.Nested(ExpressionVariableSchema), required=True
    )

    @ma.pre_dump
    def to_dict(self, data, many, **kwargs):
        return data.to_dict()


class ExpressionFullPutSchema(ExpressionFullSchema):
    class Meta(ExpressionFullSchema.Meta):
        exclude = ("campaign_scope_id",)
