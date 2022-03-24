"""Building properties API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import BuildingProperty

from bemserver_api import AutoSchema, Schema


class BuildingPropertySchema(AutoSchema):
    class Meta:
        table = BuildingProperty.__table__
        include_fk = True

    id = msa.auto_field(dump_only=True)


class BuildingPropertyQueryArgsSchema(Schema):
    structural_element_property_id = ma.fields.Int()
