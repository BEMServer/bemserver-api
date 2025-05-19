"""TaskByCampaign API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.scheduled_tasks import TaskByCampaign

from bemserver_api import AutoSchema, Schema


class TaskByCampaignSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TaskByCampaign

    id = msa.auto_field(dump_only=True)
    is_enabled = msa.auto_field(metadata={"default": True})
    parameters = ma.fields.Dict(metadata={"default": {}})


class TaskByCampaignPutSchema(Schema):
    is_enabled = ma.fields.Bool()
    parameters = ma.fields.Dict(metadata={"default": {}})


class TaskByCampaignQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
    task_name = ma.fields.String()
