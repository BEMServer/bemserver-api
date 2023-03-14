"""ST_DownloadLastWeatherData API schemas"""
import marshmallow as ma
import marshmallow_sqlalchemy as msa

from bemserver_core.scheduled_tasks import ST_DownloadLastWeatherData

from bemserver_api import AutoSchema, Schema, SortField

class ST_DownloadLastWeatherDataSchema(AutoSchema):
    pass


class ST_DownloadLastWeatherDataPutSchema(Schema):
    pass


class ST_DownloadLastWeatherDataQueryArgsSchema(Schema):
    pass


class ST_DownloadLastWeatherDataFullSchema(AutoSchema):
    pass


class ST_DownloadLastWeatherDataFullQueryArgsSchema(Schema):
    pass
