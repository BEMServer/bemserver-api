"""Event categories API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Notification

from bemserver_api import AutoSchema, Schema
from bemserver_api.extensions import ma_fields
from ..events.schemas import EventSchema


class NotificationSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Notification

    id = msa.auto_field(dump_only=True)
    event = ma.fields.Nested(EventSchema(exclude=("id",)), dump_only=True)


class NotificationPutSchema(NotificationSchema):
    class Meta(NotificationSchema.Meta):
        exclude = ("user_id", "event_id", "timestamp")


class NotificationQueryArgsSchema(Schema):
    sort = ma_fields.SortField(("timestamp",))
    user_id = ma.fields.Integer()
    event_id = ma.fields.Integer()
    campaign_id = ma.fields.Integer()
    timestamp_min = ma_fields.AwareDateTime()
    timestamp_max = ma_fields.AwareDateTime()
    read = ma.fields.Boolean()


class NotificationCountForCampaignSchema(Schema):
    campaign_id = ma.fields.Integer()
    campaign_name = ma.fields.String()
    count = ma.fields.Integer()


class NotificationCountByCampaignSchema(Schema):
    total = ma.fields.Integer()
    campaigns = ma.fields.List(ma.fields.Nested(NotificationCountForCampaignSchema))


class NotificationCountByCampaignQueryArgsSchema(Schema):
    user_id = ma.fields.Integer(required=True)
    read = ma.fields.Boolean(
        metadata={"description": "Count only read/unread. Leave empty to count all."}
    )


class NotificationMarkAllAsReadQueryArgsSchema(Schema):
    user_id = ma.fields.Integer(required=True)
    campaign_id = ma.fields.Integer()
