"""Event channels by campaigns API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventChannelByCampaign

from bemserver_api import AutoSchema


class EventChannelByCampaignSchema(AutoSchema):
    class Meta:
        table = EventChannelByCampaign.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class EventChannelByCampaignQueryArgsSchema(ma.Schema):
    campaign_id = ma.fields.Int()
    event_channel_id = ma.fields.Int()
