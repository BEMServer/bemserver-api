"""Energy production timeseries by buildings API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EnergyProductionTimeseriesByBuilding

from bemserver_api import AutoSchema, Schema
from ..timeseries.schemas import TimeseriesSchema


class EnergyProductionTimeseriesByBuildingSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EnergyProductionTimeseriesByBuilding

    id = msa.auto_field(dump_only=True)
    timeseries = ma.fields.Nested(TimeseriesSchema(exclude=("id",)), dump_only=True)


class EnergyProductionTimeseriesByBuildingQueryArgsSchema(Schema):
    building_id = ma.fields.Int()
    energy_id = ma.fields.Int()
    prod_tech_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
