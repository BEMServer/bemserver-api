"""Structural element properties API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import StructuralElementProperty
from bemserver_core.common import PropertyType

from bemserver_api import AutoSchema, Schema, SortField
from bemserver_api.extensions.ma_fields import EnumField


class StructuralElementPropertySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = StructuralElementProperty

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    value_type = EnumField(PropertyType, required=True)


class StructuralElementPropertyPutSchema(StructuralElementPropertySchema):
    class Meta(StructuralElementPropertySchema.Meta):
        exclude = ("value_type",)


class StructuralElementPropertyQueryArgsSchema(Schema):
    sort = SortField(("name",))
    name = ma.fields.Str()
    value_type = EnumField(PropertyType)
    unit_symbol = ma.fields.Str()
