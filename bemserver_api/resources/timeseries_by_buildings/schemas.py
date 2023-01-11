"""Timeseries by buildings API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesByBuilding

from bemserver_api import AutoSchema, Schema
from ..sites.schemas import SiteSchema
from ..buildings.schemas import BuildingSchema


class TimeseriesByBuildingSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesByBuilding

    id = msa.auto_field(dump_only=True)
    site = ma.fields.Nested(
        SiteSchema(exclude=("id",)), dump_only=True, attribute="building.site"
    )
    building = ma.fields.Nested(BuildingSchema(exclude=("id",)), dump_only=True)


class TimeseriesByBuildingQueryArgsSchema(Schema):
    building_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
