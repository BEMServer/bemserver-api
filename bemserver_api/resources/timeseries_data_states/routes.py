"""Timeseries data states resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesDataState

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import TimeseriesDataStateSchema


blp = Blueprint(
    "TimeseriesDataState",
    __name__,
    url_prefix="/timeseries_data_states",
    description="Operations on timeseries data states",
)


@blp.route("/")
class TimeseriesDataStatesViews(MethodView):
    @blp.login_required
    @blp.response(200, TimeseriesDataStateSchema(many=True))
    def get(self):
        """List timeseries data states"""
        return TimeseriesDataState.get()

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesDataStateSchema)
    @blp.response(201, TimeseriesDataStateSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries data state"""
        item = TimeseriesDataState.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesDataStateByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesDataStateSchema)
    def get(self, item_id):
        """Get timeseries data state by ID"""
        item = TimeseriesDataState.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesDataStateSchema)
    @blp.response(200, TimeseriesDataStateSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries data state"""
        item = TimeseriesDataState.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesDataStateSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries data state"""
        item = TimeseriesDataState.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesDataStateSchema)
        item.delete()
        db.session.commit()
