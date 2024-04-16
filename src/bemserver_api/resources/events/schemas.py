"""Events API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Event, EventLevelEnum

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields


class EventSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Event

    id = msa.auto_field(dump_only=True)
    timestamp = ma_fields.AwareDateTime()
    level = ma.fields.Enum(EventLevelEnum)


class EventPutSchema(EventSchema):
    class Meta(EventSchema.Meta):
        exclude = ("campaign_scope_id", "timestamp")


class EventQueryArgsSchema(Schema):
    sort = ma_fields.SortField(("timestamp", "level"))
    campaign_id = ma.fields.Integer()
    campaign_scope_id = ma.fields.Integer()
    user_id = ma.fields.Integer()
    source = ma.fields.String()
    in_source = ma.fields.String()
    category_id = ma.fields.Int()
    level = ma.fields.Enum(EventLevelEnum)
    level_min = ma.fields.Enum(EventLevelEnum)
    timestamp_min = ma_fields.AwareDateTime()
    timestamp_max = ma_fields.AwareDateTime()
    timeseries_id = ma.fields.Integer()
    site_id = ma.fields.Int()
    recurse_site_id = ma.fields.Int()
    building_id = ma.fields.Int()
    recurse_building_id = ma.fields.Int()
    storey_id = ma.fields.Int()
    recurse_storey_id = ma.fields.Int()
    space_id = ma.fields.Int()
    zone_id = ma.fields.Int()

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
