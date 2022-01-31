"""Events API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import (
    EventState,
    EventCategory,
    EventLevel,
    EventChannel,
    EventChannelByUser,
    EventChannelByCampaign,
)

from bemserver_api import AutoSchema


class EventStateSchema(AutoSchema):
    class Meta:
        table = EventState.__table__

    id = msa.auto_field(dump_only=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 250))


class EventCategorySchema(AutoSchema):
    class Meta:
        table = EventCategory.__table__

    id = msa.auto_field(dump_only=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 250))
    parent = msa.auto_field()


class EventLevelSchema(AutoSchema):
    class Meta:
        table = EventLevel.__table__

    id = msa.auto_field(dump_only=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 250))


class EventChannelSchema(AutoSchema):
    class Meta:
        table = EventChannel.__table__

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))


class EventChannelQueryArgsSchema(ma.Schema):
    name = ma.fields.Str()
    campaign_id = ma.fields.Int()


class EventChannelByUserSchema(AutoSchema):
    class Meta:
        table = EventChannelByUser.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class EventChannelByUserQueryArgsSchema(ma.Schema):
    user_id = ma.fields.Int()
    event_channel_id = ma.fields.Int()


class EventChannelByCampaignSchema(AutoSchema):
    class Meta:
        table = EventChannelByCampaign.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class EventChannelByCampaignQueryArgsSchema(ma.Schema):
    campaign_id = ma.fields.Int()
    event_channel_id = ma.fields.Int()
