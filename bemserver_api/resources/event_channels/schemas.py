"""Events channels API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventChannel

from bemserver_api import AutoSchema


class EventChannelSchema(AutoSchema):
    class Meta:
        table = EventChannel.__table__

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))


class EventChannelQueryArgsSchema(ma.Schema):
    name = ma.fields.Str()
    campaign_id = ma.fields.Int()
