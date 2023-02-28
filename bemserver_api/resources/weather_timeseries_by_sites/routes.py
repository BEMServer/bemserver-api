"""Weather timeseries by sites resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import WeatherTimeseriesBySite

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    WeatherTimeseriesBySiteSchema,
    WeatherTimeseriesBySiteQueryArgsSchema,
)


blp = Blueprint(
    "WeatherTimeseriesBySite",
    __name__,
    url_prefix="/weather_timeseries_by_sites",
    description="Operations on weather timeseries x site associations",
)


@blp.route("/")
class WeatherTimeseriesBySiteViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(WeatherTimeseriesBySiteQueryArgsSchema, location="query")
    @blp.response(200, WeatherTimeseriesBySiteSchema(many=True))
    def get(self, args):
        """List weather timeseries x site associations"""
        return WeatherTimeseriesBySite.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(WeatherTimeseriesBySiteSchema)
    @blp.response(201, WeatherTimeseriesBySiteSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new weather timeseries x site association"""
        item = WeatherTimeseriesBySite.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class WeatherTimeseriesBySiteByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, WeatherTimeseriesBySiteSchema)
    def get(self, item_id):
        """Get weather timeseries x site association by ID"""
        item = WeatherTimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(WeatherTimeseriesBySiteSchema)
    @blp.response(200, WeatherTimeseriesBySiteSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing weather timeseries x site association"""
        item = WeatherTimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, WeatherTimeseriesBySiteSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a weather timeseries x site association"""
        item = WeatherTimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, WeatherTimeseriesBySiteSchema)
        item.delete()
        db.session.commit()
