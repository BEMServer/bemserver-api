"""Timeseries API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Timeseries

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields


class TimeseriesSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Timeseries

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    unit_symbol = ma_fields.UnitSymbol(load_default="")


class TimeseriesPutSchema(TimeseriesSchema):
    class Meta(TimeseriesSchema.Meta):
        exclude = ("campaign_id", "campaign_scope_id")


class TimeseriesQueryArgsSchema(Schema):
    sort = ma_fields.SortField(("name",))
    name = ma.fields.String()
    in_name = ma.fields.String()
    unit_symbol = ma_fields.UnitSymbol()
    campaign_id = ma.fields.Integer()
    campaign_scope_id = ma.fields.Integer()
    user_id = ma.fields.Integer()
    site_id = ma.fields.Int()
    recurse_site_id = ma.fields.Int()
    building_id = ma.fields.Int()
    recurse_building_id = ma.fields.Int()
    storey_id = ma.fields.Int()
    recurse_storey_id = ma.fields.Int()
    space_id = ma.fields.Int()
    zone_id = ma.fields.Int()
    event_id = ma.fields.Int()

    @ma.validates_schema
    def validate_conflicting_fields(self, data, **kwargs):
        if data.get("site_id") is not None and data.get("recurse_site_id") is not None:
            raise ma.ValidationError(
                "site_id and recurse_site_id are mutually exclusive arguments"
            )
        if (
            data.get("building_id") is not None
            and data.get("recurse_building_id") is not None
        ):
            raise ma.ValidationError(
                "building_id and recurse_building_id are mutually exclusive arguments"
            )
        if (
            data.get("storey_id") is not None
            and data.get("recurse_storey_id") is not None
        ):
            raise ma.ValidationError(
                "storey_id and recurse_storey_id are mutually exclusive arguments"
            )
