"""Event categories API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Notification

from bemserver_api import AutoSchema, Schema, SortField


class NotificationSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Notification

    id = msa.auto_field(dump_only=True)


class NotificationPutSchema(NotificationSchema):
    class Meta(NotificationSchema.Meta):
        exclude = ("user_id", "event_id", "timestamp")


class NotificationsQueryArgsSchema(Schema):
    sort = SortField(("timestamp",))
    user_id = ma.fields.Integer()
    event_id = ma.fields.Integer()
    timestamp_min = ma.fields.AwareDateTime()
    timestamp_max = ma.fields.AwareDateTime()
    read = ma.fields.Boolean()
