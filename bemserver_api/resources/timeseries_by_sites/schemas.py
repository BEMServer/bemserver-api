"""Timeseries by sites API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesBySite

from bemserver_api import AutoSchema, Schema
from ..sites.schemas import SiteSchema


class TimeseriesBySiteSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = TimeseriesBySite

    id = msa.auto_field(dump_only=True)
    site = ma.fields.Nested(SiteSchema(exclude=("id",)), dump_only=True)


class TimeseriesBySiteQueryArgsSchema(Schema):
    site_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
