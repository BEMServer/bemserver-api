"""Task API schemas"""

import marshmallow as ma

from bemserver_api import Schema
from bemserver_api.extensions import ma_fields


class AsyncTaskSchema(Schema):
    name = ma.fields.String()
    default_parameters = ma.fields.Dict(keys=ma.fields.String)


class ScheduledTaskSchema(Schema):
    name = ma.fields.String()
    default_parameters = ma.fields.Dict(keys=ma.fields.String)
    schedule = ma.fields.Dict(keys=ma.fields.String, values=ma.fields.String)
    async_task = ma.fields.String()


class TaskListSchema(Schema):
    async_tasks = ma.fields.List(ma.fields.Nested(AsyncTaskSchema))
    scheduled_tasks = ma.fields.List(ma.fields.Nested(ScheduledTaskSchema))


class TaskRunArgsSchema(Schema):
    task_name = ma.fields.String(required=True)
    campaign_id = ma.fields.Int(required=True)
    start_time = ma_fields.AwareDateTime(required=True)
    end_time = ma_fields.AwareDateTime(required=True)
    parameters = ma.fields.Dict(keys=ma.fields.String)


class TaskRunResponseSchema(Schema):
    task_id = ma.fields.String()


class TaskStatusSchema(Schema):
    task_id = ma.fields.String()
    status = ma.fields.String()
    info = ma.fields.Dict(keys=ma.fields.String)
