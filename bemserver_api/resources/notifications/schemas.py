"""Event categories API schemas"""

import marshmallow_sqlalchemy as msa

from bemserver_core.model import Notification

from bemserver_api import AutoSchema


class NotificationSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Notification

    id = msa.auto_field(dump_only=True)


class NotificationPutSchema(NotificationSchema):
    class Meta(NotificationSchema.Meta):
        exclude = ("user_id", "event_id", "timestamp")
