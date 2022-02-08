"""Timeseries cluster groups by campaigns resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesClusterGroupByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TimeseriesClusterGroupByCampaignSchema,
    TimeseriesClusterGroupByCampaignQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesClusterGroupByCampaign",
    __name__,
    url_prefix="/timeseries_cluster_groups_by_campaigns",
    description="Operations on timeseries cluster groups x campaigns associations",
)


@blp.route("/")
class TimeseriesClusterGroupByCampaignViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterGroupByCampaignQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesClusterGroupByCampaignSchema(many=True))
    def get(self, args):
        """List campaign x timeseries cluster groups associations"""
        return TimeseriesClusterGroupByCampaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterGroupByCampaignSchema)
    @blp.response(201, TimeseriesClusterGroupByCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new campaign x timeseries cluster groups association"""
        item = TimeseriesClusterGroupByCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesClusterGroupByCampaignByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesClusterGroupByCampaignSchema)
    def get(self, item_id):
        """Get campaign x timeseries cluster groups association by ID"""
        item = TimeseriesClusterGroupByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a campaign x timeseries cluster groups association"""
        item = TimeseriesClusterGroupByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
