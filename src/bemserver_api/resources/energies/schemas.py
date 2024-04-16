"""Energies API schemas"""

import marshmallow_sqlalchemy as msa

from bemserver_core.model import Energy

from bemserver_api import AutoSchema


class EnergySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = Energy

    id = msa.auto_field(dump_only=True)
