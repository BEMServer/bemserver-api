"""Event categories API schemas"""

import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventCategory

from bemserver_api import AutoSchema


class EventCategorySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = EventCategory.__table__

    id = msa.auto_field(dump_only=True)
    parent = msa.auto_field()
