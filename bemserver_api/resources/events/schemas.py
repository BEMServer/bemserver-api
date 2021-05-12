"""Events API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import (
    EventState, EventCategory, EventLevel, EventTarget, Event)

from bemserver_api import Schema, AutoSchema


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


class EventTargetSchema(AutoSchema):
    class Meta:
        table = EventTarget.__table__

    id = msa.auto_field(dump_only=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 250))


class EventSchema(AutoSchema):
    class Meta:
        table = Event.__table__

    id = msa.auto_field(dump_only=True)
    category = msa.auto_field()
    level = msa.auto_field()
    timestamp_start = msa.auto_field()
    timestamp_end = msa.auto_field()
    source = msa.auto_field()
    target_type = msa.auto_field()
    target_id = msa.auto_field()
    state = msa.auto_field()
    timestamp_last_update = msa.auto_field()


class EventPostArgsSchema(Schema):

    source = ma.fields.Str(required=True)
    category = ma.fields.Str(required=True)
    target_type = ma.fields.Str(required=True)
    target_id = ma.fields.Int(required=True)
    level = ma.fields.Str()
    timestamp_start = ma.fields.AwareDateTime()
    description = ma.fields.Str()


class EventClosePostArgsSchema(Schema):

    timestamp_end = ma.fields.AwareDateTime()


class EventQueryArgsSchema(Schema):
    source = ma.fields.Str()
    category = ma.fields.Str()
    target_type = ma.fields.Str()
    target_id = ma.fields.Int()
    level = ma.fields.Str()
    state = ma.fields.Str()
