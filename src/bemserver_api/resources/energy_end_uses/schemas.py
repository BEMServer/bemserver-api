"""Energy end uses API schemas"""

import marshmallow_sqlalchemy as msa

from bemserver_core.model import EnergyEndUse

from bemserver_api import AutoSchema


class EnergyEndUseSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = EnergyEndUse

    id = msa.auto_field(dump_only=True)
