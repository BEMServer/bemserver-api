"""ST_DownloadLastWeatherData API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.scheduled_tasks import ST_DownloadLastWeatherData

from bemserver_api import AutoSchema, Schema, SortField

class ST_DownloadLastWeatherDataSchema(AutoSchema):
    class Meta(AutoSchema.Meta):
        model = ST_DownloadLastWeatherData

    id = msa.auto_field(dump_only=True)
    is_enabled = msa.auto_field(metadata={"default": True})


class ST_DownloadLastWeatherDataPutSchema(Schema):
    is_enabled = ma.fields.Boolean()


class ST_DownloadLastWeatherDataFullSchema(Schema):
    id = ma.fields.Integer(dump_only=True)
    site_id = ma.fields.Integer(dump_only=True)
    is_enabled = ma.fields.Boolean(dump_only=True)


class ST_DownloadLastWeatherDataQueryArgsSchema(Schema):
    pass


class ST_DownloadLastWeatherDataFullQueryArgsSchema(Schema):
    pass