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
    campaign_id = ma.fields.Int(required=True)
    campaign_scope_id = ma.fields.Int(required=True)
    unit_symbol = msa.auto_field()


class TimeseriesPutSchema(TimeseriesSchema):
    class Meta(TimeseriesSchema.Meta):
        exclude = ("campaign_id", "campaign_scope_id")


class TimeseriesQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
    in_name = ma.fields.Str()
    unit_symbol = ma.fields.Str()
    campaign_id = ma.fields.Int()
    campaign_scope_id = ma.fields.Int()
    user_id = ma.fields.Int()
    site_id = ma.fields.Int()
    building_id = ma.fields.Int()
    storey_id = ma.fields.Int()
    space_id = ma.fields.Int()
    zone_id = ma.fields.Int()
