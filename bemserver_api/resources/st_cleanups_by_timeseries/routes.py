"""ST_CleanupByTimeseries resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.scheduled_tasks import ST_CleanupByTimeseries

from bemserver_api import Blueprint

from .schemas import (
    ST_CleanupByTimeseriesSchema,
    ST_CleanupByTimeseriesQueryArgsSchema,
    ST_CleanupByTimeseriesFullSchema,
    ST_CleanupByTimeseriesFullQueryArgsSchema,
)


blp = Blueprint(
    "ST_CleanupByTimeseries",
    __name__,
    url_prefix="/st_cleanups_by_timeseries",
    description="Operations on cleanup scheduled task x timeseries associations",
)


@blp.route("/")
class ST_CleanupByTimeseriesViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ST_CleanupByTimeseriesQueryArgsSchema, location="query")
    @blp.response(200, ST_CleanupByTimeseriesSchema(many=True))
    def get(self, args):
        """List cleanup scheduled task x timeseries associations"""
        return ST_CleanupByTimeseries.get(**args)


@blp.route("/<int:item_id>")
class ST_CleanupByTimeseriesByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ST_CleanupByTimeseriesSchema)
    def get(self, item_id):
        """Get cleanup scheduled task x timeseries association by ID"""
        item = ST_CleanupByTimeseries.get_by_id(item_id)
        if item is None:
            abort(404)
        return item


@blp.route("/full")
@blp.login_required
@blp.etag
@blp.arguments(ST_CleanupByTimeseriesFullQueryArgsSchema, location="query")
@blp.response(200, ST_CleanupByTimeseriesFullSchema(many=True))
def get_full(args):
    """List cleanup service last timestamp for all timeseries"""
    return ST_CleanupByTimeseries.get_all(**args)
