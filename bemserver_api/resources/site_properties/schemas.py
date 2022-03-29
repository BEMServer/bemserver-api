"""Site properties API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import SiteProperty

from bemserver_api import AutoSchema, Schema


class SitePropertySchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = SiteProperty.__table__

    id = msa.auto_field(dump_only=True)


class SitePropertyQueryArgsSchema(Schema):
    structural_element_property_id = ma.fields.Int()
