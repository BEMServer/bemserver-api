"""Task API schemas"""

import marshmallow as ma

from bemserver_api import Schema


class TasksSchema(Schema):
    tasks = ma.fields.List(ma.fields.String)
