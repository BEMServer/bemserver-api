"""Events by storeys API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventByStorey

from bemserver_api import AutoSchema, Schema
from ..sites.schemas import SiteSchema
from ..buildings.schemas import BuildingSchema
from ..storeys.schemas import StoreySchema


class EventByStoreySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EventByStorey

    id = msa.auto_field(dump_only=True)
    site = ma.fields.Nested(
        SiteSchema(exclude=("id",)), dump_only=True, attribute="storey.building.site"
    )
    building = ma.fields.Nested(
        BuildingSchema(exclude=("id",)), dump_only=True, attribute="storey.building"
    )
    storey = ma.fields.Nested(StoreySchema(exclude=("id",)), dump_only=True)


class EventByStoreyQueryArgsSchema(Schema):
    storey_id = ma.fields.Int()
    event_id = ma.fields.Int()
