"""Expression variables API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.common import AggregationFunctionsEnum
from bemserver_core.model import ExpressionVariable

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields


class ExpressionVariableSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ExpressionVariable

    id = msa.auto_field(dump_only=True)
    aggregation = ma.fields.Enum(
        AggregationFunctionsEnum,
        load_default=AggregationFunctionsEnum.AVG,
        by_value=True,
    )


class ExpressionVariablePutSchema(ExpressionVariableSchema):
    class Meta(ExpressionVariableSchema.Meta):
        exclude = ("campaign_scope_id", "expression_id")


class ExpressionVariableQueryArgsSchema(Schema):
    sort = ma_fields.SortField(("name",))
    campaign_scope_id = ma.fields.Int()
    expression_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
