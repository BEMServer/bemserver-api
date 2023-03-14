"""ST_DownloadLastWeatherData resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.scheduled_tasks import ST_DownloadLastWeatherData

from bemserver_api import Blueprint

from .schemas import (
    ST_DownloadLastWeatherDataSchema,
    ST_DownloadLastWeatherDataPutSchema,
    ST_DownloadLastWeatherDataQueryArgsSchema,
    ST_DownloadLastWeatherDataFullSchema,
    ST_DownloadLastWeatherDataFullQueryArgsSchema,
)

blp = Blueprint(
    "ST_DownloadLastWeatherData",
    __name__,
    url_prefix="/st_download_last_weather_data",
    description="Operations on download last weather data scheduled task",
)

@blp.route("/")
class ST_DownloadLastWeatherDataViews(MethodView):
    pass