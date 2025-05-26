"""TaskByCampaign API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TaskByCampaign
from bemserver_core.time_utils import PeriodEnum

from bemserver_api import AutoSchema, Schema


class TaskByCampaignSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TaskByCampaign

    id = msa.auto_field(dump_only=True)
    is_enabled = msa.auto_field(metadata={"default": True})
    parameters = ma.fields.Dict(metadata={"default": {}})
    offset_unit = ma.fields.Enum(PeriodEnum)


class TaskByCampaignPutSchema(TaskByCampaignSchema):
    class Meta(TaskByCampaignSchema.Meta):
        exclude = ("campaign_id", "task_name")


class TaskByCampaignQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
    task_name = ma.fields.String()
    is_enabled = ma.fields.Boolean()
