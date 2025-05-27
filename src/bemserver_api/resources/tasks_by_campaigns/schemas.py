"""TaskByCampaign API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TaskByCampaign
from bemserver_core.time_utils import PeriodEnum

from bemserver_api import AutoSchema, Schema


class TaskByCampaignBaseSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TaskByCampaign

    id = msa.auto_field(dump_only=True)
    is_enabled = msa.auto_field(metadata={"default": True})
    parameters = ma.fields.Dict(metadata={"default": {}})
    offset_unit = ma.fields.Enum(PeriodEnum)


class TaskByCampaignSchema(TaskByCampaignBaseSchema):
    @ma.post_load
    def add_scheduled_suffix(self, item, many, **kwargs):
        item["task_name"] = f"{item['task_name']}Scheduled"
        return item

    @ma.post_dump
    def remove_scheduled_suffix(self, data, many, **kwargs):
        data["task_name"] = data["task_name"].removesuffix("Scheduled")
        return data


class TaskByCampaignPutSchema(TaskByCampaignBaseSchema):
    class Meta(TaskByCampaignSchema.Meta):
        exclude = ("campaign_id", "task_name")


class TaskByCampaignQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
    task_name = ma.fields.String()
    is_enabled = ma.fields.Boolean()
