"""Timeseries properties API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import TimeseriesProperty
from bemserver_core.common import PropertyType

from bemserver_api import AutoSchema
from bemserver_api.extensions.ma_fields import EnumField


class TimeseriesPropertySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = TimeseriesProperty.__table__

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    value_type = EnumField(
        validate=ma.validate.OneOf([x.name for x in PropertyType]),
        required=True,
    )


class TimeseriesPropertyPutSchema(TimeseriesPropertySchema):
    class Meta(TimeseriesPropertySchema.Meta):
        exclude = ("value_type",)
