"""Events by buildings API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventByBuilding

from bemserver_api import AutoSchema, Schema
from ..sites.schemas import SiteSchema
from ..buildings.schemas import BuildingSchema


class EventByBuildingSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EventByBuilding

    id = msa.auto_field(dump_only=True)
    site = ma.fields.Nested(
        SiteSchema(exclude=("id",)), dump_only=True, attribute="building.site"
    )
    building = ma.fields.Nested(BuildingSchema(exclude=("id",)), dump_only=True)


class EventByBuildingQueryArgsSchema(Schema):
    building_id = ma.fields.Int()
    event_id = ma.fields.Int()
