"""Events by spaces API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventBySpace

from bemserver_api import AutoSchema, Schema
from ..sites.schemas import SiteSchema
from ..buildings.schemas import BuildingSchema
from ..storeys.schemas import StoreySchema
from ..spaces.schemas import SpaceSchema


class EventBySpaceSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EventBySpace

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


class EventBySpaceQueryArgsSchema(Schema):
    space_id = ma.fields.Int()
    event_id = ma.fields.Int()
