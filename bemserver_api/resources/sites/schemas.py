"""Sites API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.model import Site

from bemserver_api import AutoSchema, Schema


class SiteSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        table = Site.__table__
        exclude = ("_campaign_id",)

    id = msa.auto_field(dump_only=True)
    name = msa.auto_field(validate=ma.validate.Length(1, 80))
    campaign_id = ma.fields.Int(required=True)
    description = msa.auto_field(validate=ma.validate.Length(1, 500))


class SitePutSchema(SiteSchema):
    class Meta(SiteSchema.Meta):
        exclude = SiteSchema.Meta.exclude + ("campaign_id",)


class SiteQueryArgsSchema(Schema):
    name = ma.fields.Str()
    campaign_id = ma.fields.Int()
    ifc_id = ma.fields.String()
