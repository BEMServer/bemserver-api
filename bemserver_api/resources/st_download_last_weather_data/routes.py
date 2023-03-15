"""ST_DownloadLastWeatherData resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.scheduled_tasks import ST_DownloadLastWeatherData

from bemserver_api import Blueprint
from bemserver_api.database import db

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
    @blp.login_required
    @blp.etag
    @blp.arguments(ST_DownloadLastWeatherDataQueryArgsSchema, location="query")
    @blp.response(200, ST_DownloadLastWeatherDataSchema(many=True))
    def get(self, args):
        """List download last weather data scheduled tasks"""
        return ST_DownloadLastWeatherData.get(**args)
    
    @blp.login_required
    @blp.etag
    @blp.arguments(ST_DownloadLastWeatherDataSchema)
    @blp.response(201, ST_DownloadLastWeatherDataSchema)
    @blp.catch_integrity_error
    def post(self, new_data):
        """Create a new download last weather data scheduled task"""
        data = ST_DownloadLastWeatherData.new(**new_data)
        db.session.commit()
        return data
    

@blp.route("/<int:item_id>")
class ST_DownloadLastWeatherDataItemViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ST_DownloadLastWeatherDataSchema)
    def get(self, item_id):
        """Get download last weather data scheduled task details"""
        item = ST_DownloadLastWeatherData.get_by_id(item_id)
        if item is None:
            abort(404)
        return item
    
    @blp.login_required
    @blp.etag
    @blp.arguments(ST_DownloadLastWeatherDataPutSchema)
    @blp.response(200, ST_DownloadLastWeatherDataSchema)
    def put(self, update_data, item_id):
        """Update download last weather data scheduled task details"""
        item = ST_DownloadLastWeatherData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_DownloadLastWeatherDataSchema)
        item.update(**update_data)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a download last weather data scheduled task"""
        item = ST_DownloadLastWeatherData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_DownloadLastWeatherDataSchema)
        item.delete()
        db.session.commit()


@blp.route("/full")
@blp.login_required
@blp.etag
@blp.arguments(ST_DownloadLastWeatherDataFullQueryArgsSchema, location="query")
@blp.response(200, ST_DownloadLastWeatherDataFullSchema(many=True))
def get_full(args):
    """List download last weather data scheduled tasks with full details"""
    return ST_DownloadLastWeatherData.get_all(**args)