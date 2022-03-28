"""Space properties API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import SpaceProperty

from bemserver_api import AutoSchema, Schema


class SpacePropertySchema(AutoSchema):
    class Meta:
        table = SpaceProperty.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class SpacePropertyQueryArgsSchema(Schema):
    structural_element_property_id = ma.fields.Int()
