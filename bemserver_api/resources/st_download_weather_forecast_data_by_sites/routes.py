"""ST_DownloadWeatherForecastDataBySite resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.scheduled_tasks import ST_DownloadWeatherForecastDataBySite

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    ST_DownloadWeatherForecastDataBySiteSchema,
    ST_DownloadWeatherForecastDataBySiteQueryArgsSchema,
    ST_DownloadWeatherForecastDataBySitePutSchema,
    ST_DownloadWeatherForecastDataBySiteFullSchema,
    ST_DownloadWeatherForecastDataBySiteFullQueryArgsSchema,
)


blp = Blueprint(
    "ST_DownloadWeatherForecastDataBySite",
    __name__,
    url_prefix="/st_download_weather_forecast_data_by_sites",
    description=(
        "Operations on download weather forecast data scheduled task "
        "x site associations"
    ),
)


@blp.route("/")
class ST_DownloadWeatherForecastDataBySiteViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(
        ST_DownloadWeatherForecastDataBySiteQueryArgsSchema, location="query"
    )
    @blp.response(200, ST_DownloadWeatherForecastDataBySiteSchema(many=True))
    def get(self, args):
        """List download weather forecast data scheduled tasks x site associations"""
        return ST_DownloadWeatherForecastDataBySite.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(ST_DownloadWeatherForecastDataBySiteSchema)
    @blp.response(201, ST_DownloadWeatherForecastDataBySiteSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new download weather forecast data scheduled task x site association"""
        item = ST_DownloadWeatherForecastDataBySite.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class ST_DownloadWeatherForecastDataBySiteByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ST_DownloadWeatherForecastDataBySiteSchema)
    def get(self, item_id):
        """Get download weather forecast data scheduled task x site association by ID"""
        item = ST_DownloadWeatherForecastDataBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(ST_DownloadWeatherForecastDataBySitePutSchema)
    @blp.response(200, ST_DownloadWeatherForecastDataBySiteSchema)
    def put(self, item_data, item_id):
        """Update a download weather forecast data scheduled task x site association"""
        item = ST_DownloadWeatherForecastDataBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_DownloadWeatherForecastDataBySiteSchema)
        item.update(**item_data)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a download weather forecast data scheduled task x site association"""
        item = ST_DownloadWeatherForecastDataBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_DownloadWeatherForecastDataBySiteSchema)
        item.delete()
        db.session.commit()


@blp.route("/full")
@blp.login_required
@blp.etag
@blp.arguments(
    ST_DownloadWeatherForecastDataBySiteFullQueryArgsSchema, location="query"
)
@blp.response(200, ST_DownloadWeatherForecastDataBySiteFullSchema(many=True))
def get_full(args):
    """List download weather forecast data service state for all sites"""
    return ST_DownloadWeatherForecastDataBySite.get_all(**args)
