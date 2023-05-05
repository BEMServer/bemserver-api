"""ST_DownloadWeatherDataBySite resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.scheduled_tasks import ST_DownloadWeatherDataBySite

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    ST_DownloadWeatherDataBySiteSchema,
    ST_DownloadWeatherDataBySiteQueryArgsSchema,
    ST_DownloadWeatherDataBySitePutSchema,
    ST_DownloadWeatherDataBySiteFullSchema,
    ST_DownloadWeatherDataBySiteFullQueryArgsSchema,
)


blp = Blueprint(
    "ST_DownloadWeatherDataBySite",
    __name__,
    url_prefix="/st_download_weather_data_by_sites",
    description=(
        "Operations on download weather data scheduled task x site associations"
    ),
)


@blp.route("/")
class ST_DownloadWeatherDataBySiteViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ST_DownloadWeatherDataBySiteQueryArgsSchema, location="query")
    @blp.response(200, ST_DownloadWeatherDataBySiteSchema(many=True))
    def get(self, args):
        """List download weather data scheduled tasks x site associations"""
        return ST_DownloadWeatherDataBySite.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(ST_DownloadWeatherDataBySiteSchema)
    @blp.response(201, ST_DownloadWeatherDataBySiteSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new download weather data scheduled task x site association"""
        item = ST_DownloadWeatherDataBySite.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class ST_DownloadWeatherDataBySiteByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ST_DownloadWeatherDataBySiteSchema)
    def get(self, item_id):
        """Get download weather data scheduled task x site association by ID"""
        item = ST_DownloadWeatherDataBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(ST_DownloadWeatherDataBySitePutSchema)
    @blp.response(200, ST_DownloadWeatherDataBySiteSchema)
    def put(self, item_data, item_id):
        """Update a download weather data scheduled task x site association"""
        item = ST_DownloadWeatherDataBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_DownloadWeatherDataBySiteSchema)
        item.update(**item_data)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a download weather data scheduled task x site association"""
        item = ST_DownloadWeatherDataBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_DownloadWeatherDataBySiteSchema)
        item.delete()
        db.session.commit()


@blp.route("/full")
@blp.login_required
@blp.etag
@blp.arguments(ST_DownloadWeatherDataBySiteFullQueryArgsSchema, location="query")
@blp.response(200, ST_DownloadWeatherDataBySiteFullSchema(many=True))
def get_full(args):
    """List download weather data service state for all sites"""
    return ST_DownloadWeatherDataBySite.get_all(**args)
