"""Event states API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventState

from bemserver_api import AutoSchema


class EventStateSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = EventState.__table__

    id = msa.auto_field(dump_only=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 250))
