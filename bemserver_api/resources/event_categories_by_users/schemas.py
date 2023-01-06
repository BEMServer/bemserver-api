"""Even categories by users API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EventLevelEnum, EventCategoryByUser

from bemserver_api import AutoSchema, Schema


class EventCategoryByUserSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EventCategoryByUser

    id = msa.auto_field(dump_only=True)
    notification_level = ma.fields.Enum(EventLevelEnum)


class EventCategoryByUserPutSchema(EventCategoryByUserSchema):
    class Meta(EventCategoryByUserSchema.Meta):
        exclude = ("user_id",)


class EventCategoryByUserQueryArgsSchema(Schema):
    category_id = ma.fields.Int()
    user_id = ma.fields.Int()
