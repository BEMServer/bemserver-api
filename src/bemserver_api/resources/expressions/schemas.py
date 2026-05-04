"""Expressions API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Expression

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
