"""Events channels by users API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventChannelByUser

from bemserver_api import AutoSchema


class EventChannelByUserSchema(AutoSchema):
    class Meta:
        table = EventChannelByUser.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class EventChannelByUserQueryArgsSchema(ma.Schema):
    user_id = ma.fields.Int()
    event_channel_id = ma.fields.Int()
