"""Timeseries groups by campaigns resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesGroupByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TimeseriesGroupByCampaignSchema,
    TimeseriesGroupByCampaignQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesGroupByCampaign",
    __name__,
    url_prefix="/timeseries_groups_by_campaigns",
    description="Operations on timeseries groups x campaigns associations",
)


@blp.route("/")
class TimeseriesGroupByCampaignViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesGroupByCampaignQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesGroupByCampaignSchema(many=True))
    def get(self, args):
        """List campaign x timeseries groups associations"""
        return TimeseriesGroupByCampaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesGroupByCampaignSchema)
    @blp.response(201, TimeseriesGroupByCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new campaign x timeseries groups association"""
        item = TimeseriesGroupByCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesGroupByCampaignByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesGroupByCampaignSchema)
    def get(self, item_id):
        """Get campaign x timeseries groups association by ID"""
        item = TimeseriesGroupByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a campaign x timeseries groups association"""
        item = TimeseriesGroupByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
