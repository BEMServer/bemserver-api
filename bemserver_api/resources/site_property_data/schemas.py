"""Site property data API schemas"""

import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import SitePropertyData

from bemserver_api import AutoSchema, Schema


class SitePropertyDataSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = SitePropertyData

    id = msa.auto_field(dump_only=True)


class SitePropertyDataQueryArgsSchema(Schema):
    site_id = ma.fields.Int()
    site_property_id = ma.fields.Int()
