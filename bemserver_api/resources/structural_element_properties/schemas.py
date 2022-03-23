"""Structural element properties API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import StructuralElementProperty

from bemserver_api import AutoSchema, Schema


class StructuralElementPropertySchema(AutoSchema):
    class Meta:
        table = StructuralElementProperty.__table__

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))


class StructuralElementPropertyQueryArgsSchema(Schema):
    name = ma.fields.Str()
