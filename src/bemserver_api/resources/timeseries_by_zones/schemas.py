"""Timeseries by zones API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesByZone

from bemserver_api import AutoSchema, Schema

from ..zones.schemas import ZoneSchema


class TimeseriesByZoneSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesByZone

    id = msa.auto_field(dump_only=True)
    zone = ma.fields.Nested(ZoneSchema(exclude=("id",)), dump_only=True)


class TimeseriesByZoneQueryArgsSchema(Schema):
    zone_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
