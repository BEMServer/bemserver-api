"""Energy sources API schemas"""

import marshmallow_sqlalchemy as msa

from bemserver_core.model import EnergySource

from bemserver_api import AutoSchema


class EnergySourceSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = EnergySource.__table__

    id = msa.auto_field(dump_only=True)
