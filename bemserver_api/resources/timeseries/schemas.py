"""Timeseries API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Timeseries

from bemserver_api import AutoSchema, Schema, SortField


class TimeseriesSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Timeseries

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))


class TimeseriesPutSchema(TimeseriesSchema):
    class Meta(TimeseriesSchema.Meta):
        exclude = ("campaign_id", "campaign_scope_id")


class TimeseriesQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.String()
    in_name = ma.fields.String()
    unit_symbol = ma.fields.String()
    campaign_id = ma.fields.Integer()
    campaign_scope_id = ma.fields.Integer()
    user_id = ma.fields.Integer()


class TimeseriesRecurseArgsSchema(Schema):
    recurse = ma.fields.Boolean()
