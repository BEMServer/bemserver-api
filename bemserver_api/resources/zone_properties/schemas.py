"""Zone properties API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import ZoneProperty

from bemserver_api import AutoSchema, Schema


class ZonePropertySchema(AutoSchema):
    class Meta:
        table = ZoneProperty.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class ZonePropertyQueryArgsSchema(Schema):
    structural_element_property_id = ma.fields.Int()
