"""Event categories API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventCategory

from bemserver_api import AutoSchema


class EventCategorySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = EventCategory.__table__

    id = msa.auto_field(dump_only=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 250))
    parent = msa.auto_field()
