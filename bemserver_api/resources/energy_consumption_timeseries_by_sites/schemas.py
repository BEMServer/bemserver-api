"""Energy consumption timeseries by sites API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EnergyConsumptionTimeseriesBySite

from bemserver_api import AutoSchema, Schema
from ..timeseries.schemas import TimeseriesSchema


class EnergyConsumptionTimeseriesBySiteSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EnergyConsumptionTimeseriesBySite

    id = msa.auto_field(dump_only=True)
    timeseries = ma.fields.Nested(TimeseriesSchema(exclude=("id",)), dump_only=True)


class EnergyConsumptionTimeseriesBySiteQueryArgsSchema(Schema):
    site_id = ma.fields.Int()
    energy_id = ma.fields.Int()
    end_use_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
