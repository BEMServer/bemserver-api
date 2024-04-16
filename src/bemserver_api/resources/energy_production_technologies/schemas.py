"""Energy production technologies API schemas"""

import marshmallow_sqlalchemy as msa

from bemserver_core.model import EnergyProductionTechnology

from bemserver_api import AutoSchema


class EnergyProductionTechnologySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EnergyProductionTechnology

    id = msa.auto_field(dump_only=True)
