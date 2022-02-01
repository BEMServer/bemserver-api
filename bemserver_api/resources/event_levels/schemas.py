"""Event levels API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventLevel

from bemserver_api import AutoSchema


class EventLevelSchema(AutoSchema):
    class Meta:
        table = EventLevel.__table__

    id = msa.auto_field(dump_only=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 250))
