"""Event levels API schemas"""

import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventLevel

from bemserver_api import AutoSchema


class EventLevelSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EventLevel

    id = msa.auto_field(dump_only=True)
