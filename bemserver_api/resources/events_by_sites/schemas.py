"""Events by sites API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventBySite

from bemserver_api import AutoSchema, Schema


class EventBySiteSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EventBySite

    id = msa.auto_field(dump_only=True)


class EventBySiteQueryArgsSchema(Schema):
    site_id = ma.fields.Int()
    event_id = ma.fields.Int()
