"""Energy production timeseries by sites API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import EnergyProductionTimeseriesBySite

from bemserver_api import AutoSchema, Schema


class EnergyProductionTimeseriesBySiteSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EnergyProductionTimeseriesBySite

    id = msa.auto_field(dump_only=True)


class EnergyProductionTimeseriesBySiteQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int()
    site_id = ma.fields.Int()
    source_id = ma.fields.Int()
    end_use_id = ma.fields.Int()
    timeseries_id = ma.fields.Int()
