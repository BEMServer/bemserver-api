"""Timeseries expressions API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesExpression
from bemserver_core.time_utils import PeriodEnum

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields


class TimeseriesExpressionSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesExpression

    id = msa.auto_field(dump_only=True)
    bucket_width_unit = ma.fields.Enum(PeriodEnum)
    timezone = ma_fields.Timezone(load_default="UTC")


class TimeseriesExpressionPutSchema(TimeseriesExpressionSchema):
    class Meta(TimeseriesExpressionSchema.Meta):
        exclude = ("campaign_scope_id", "expression_id")


class TimeseriesExpressionQueryArgsSchema(Schema):
    sort = ma_fields.SortField(("id",))
    campaign_scope_id = ma.fields.Int()
    expression_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
