"""Timeseries by events resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesByEvent
from bemserver_core.exceptions import BEMServerCoreCampaignScopeError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TimeseriesByEventSchema,
    TimeseriesByEventQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesByEvent",
    __name__,
    url_prefix="/timeseries_by_events",
    description="Operations on timeseries x event associations",
)


@blp.route("/")
class TimeseriesByEventViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesByEventQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesByEventSchema(many=True))
    def get(self, args):
        """List timeseries x event associations"""
        return TimeseriesByEvent.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesByEventSchema)
    @blp.response(201, TimeseriesByEventSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries x event association"""
        item = TimeseriesByEvent.new(**new_item)
        try:
            db.session.commit()
        except BEMServerCoreCampaignScopeError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item


@blp.route("/<int:item_id>")
class TimeseriesByEventByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesByEventSchema)
    def get(self, item_id):
        """Get timeseries x event association ID"""
        item = TimeseriesByEvent.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries x event association"""
        item = TimeseriesByEvent.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
