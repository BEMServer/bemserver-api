"""Campaigns API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Campaign

from bemserver_api import AutoSchema, Schema, SortField


class CampaignSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = Campaign.__table__

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    start_time = ma.fields.AwareDateTime()
    end_time = ma.fields.AwareDateTime()


class CampaignQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
    in_name = ma.fields.Str(
        metadata={
            "description": """
Search for items whose name contains this input value (case insensitive)""",
        }
    )
