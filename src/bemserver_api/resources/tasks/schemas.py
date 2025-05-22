"""Task API schemas"""

import marshmallow as ma

from bemserver_api import Schema
from bemserver_api.extensions import ma_fields


class TaskSchema(Schema):
    name = ma.fields.String()
    default_parameters = ma.fields.Dict(keys=ma.fields.String)


class TasksSchema(Schema):
    async_tasks = ma.fields.List(ma.fields.Nested(TaskSchema))
    scheduled_tasks = ma.fields.List(ma.fields.Nested(TaskSchema))


class TaskRunSchema(Schema):
    task_name = ma.fields.String(required=True)
    campaign_id = ma.fields.Int(required=True)
    start_time = ma_fields.AwareDateTime(required=True)
    end_time = ma_fields.AwareDateTime(required=True)
    parameters = ma.fields.Dict(keys=ma.fields.String)
