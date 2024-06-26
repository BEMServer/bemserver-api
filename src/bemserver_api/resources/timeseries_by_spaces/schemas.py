"""Timeseries by spaces API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesBySpace

from bemserver_api import AutoSchema, Schema

from ..buildings.schemas import BuildingSchema
from ..sites.schemas import SiteSchema
from ..spaces.schemas import SpaceSchema
from ..storeys.schemas import StoreySchema


class TimeseriesBySpaceSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesBySpace

    id = msa.auto_field(dump_only=True)
    site = ma.fields.Nested(
        SiteSchema(exclude=("id",)),
        dump_only=True,
        attribute="space.storey.building.site",
    )
    building = ma.fields.Nested(
        BuildingSchema(exclude=("id",)),
        dump_only=True,
        attribute="space.storey.building",
    )
    storey = ma.fields.Nested(
        StoreySchema(exclude=("id",)), dump_only=True, attribute="space.storey"
    )
    space = ma.fields.Nested(SpaceSchema(exclude=("id",)), dump_only=True)


class TimeseriesBySpaceQueryArgsSchema(Schema):
    space_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
