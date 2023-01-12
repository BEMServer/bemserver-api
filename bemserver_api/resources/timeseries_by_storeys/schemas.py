"""Timeseries by storeys API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesByStorey

from bemserver_api import AutoSchema, Schema
from ..sites.schemas import SiteSchema
from ..buildings.schemas import BuildingSchema
from ..storeys.schemas import StoreySchema


class TimeseriesByStoreySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesByStorey

    id = msa.auto_field(dump_only=True)
    site = ma.fields.Nested(
        SiteSchema(exclude=("id",)), dump_only=True, attribute="storey.building.site"
    )
    building = ma.fields.Nested(
        BuildingSchema(exclude=("id",)), dump_only=True, attribute="storey.building"
    )
    storey = ma.fields.Nested(StoreySchema(exclude=("id",)), dump_only=True)


class TimeseriesByStoreyQueryArgsSchema(Schema):
    storey_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
