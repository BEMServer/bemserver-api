"""Site resources"""
import http

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Site
from bemserver_core.process.weather import wdp
from bemserver_core.exceptions import (
    BEMServerCoreSettingsError,
    BEMServerCoreWeatherAPIAuthenticationError,
    BEMServerCoreWeatherProcessMissingCoordinatesError,
)
from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    SiteSchema,
    SitePutSchema,
    SiteQueryArgsSchema,
    DownloadWeatherDataQueryArgsSchema,
)


blp = Blueprint(
    "Site", __name__, url_prefix="/sites", description="Operations on sites"
)


@blp.route("/")
class SiteViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(SiteQueryArgsSchema, location="query")
    @blp.response(200, SiteSchema(many=True))
    def get(self, args):
        """List sites"""
        return Site.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(SiteSchema)
    @blp.response(201, SiteSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new site"""
        item = Site.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class SiteByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, SiteSchema)
    def get(self, item_id):
        """Get site by ID"""
        item = Site.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(SitePutSchema)
    @blp.response(200, SiteSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing site"""
        item = Site.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, SiteSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a site"""
        item = Site.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, SiteSchema)
        item.delete()
        db.session.commit()


@blp.route("/<int:item_id>/download_weather_data", methods=["PUT"])
@blp.login_required
@blp.arguments(DownloadWeatherDataQueryArgsSchema, location="query")
@blp.response(204)
@blp.alt_response(409, http.HTTPStatus(409).name)
def download_weather_data(args, item_id):
    item = Site.get_by_id(item_id)
    if item is None:
        abort(404)
    try:
        wdp.get_weather_data_for_site(item, args["start_time"], args["end_time"])
    except (
        BEMServerCoreSettingsError,
        BEMServerCoreWeatherProcessMissingCoordinatesError,
        BEMServerCoreWeatherAPIAuthenticationError,
    ) as exc:
        abort(409, message=str(exc))
    db.session.commit()
