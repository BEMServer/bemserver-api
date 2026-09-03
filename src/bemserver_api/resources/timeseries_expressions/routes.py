"""Timeseries expressions resources"""

from flask.views import MethodView

from flask_smorest import abort

from bemserver_core.exceptions import BEMServerCoreCampaignScopeError
from bemserver_core.model import TimeseriesExpression

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    TimeseriesExpressionPutSchema,
    TimeseriesExpressionQueryArgsSchema,
    TimeseriesExpressionSchema,
)

blp = Blueprint(
    "TimeseriesExpression",
    __name__,
    url_prefix="/timeseries_expressions",
    description="Operations on timeseries expressions",
)


@blp.route("/")
class TimeseriesExpressionViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesExpressionQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesExpressionSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List timeseries expressions"""
        return TimeseriesExpression.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesExpressionSchema)
    @blp.response(201, TimeseriesExpressionSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries expression"""
        item = TimeseriesExpression.new(**new_item)
        try:
            db.session.commit()
        except BEMServerCoreCampaignScopeError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item


@blp.route("/<int:item_id>")
class TimeseriesExpressionByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesExpressionSchema)
    def get(self, item_id):
        """Get timeseries expression by ID"""
        item = TimeseriesExpression.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesExpressionPutSchema)
    @blp.response(200, TimeseriesExpressionSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries expression"""
        item = TimeseriesExpression.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesExpressionSchema)
        try:
            item.update(**new_item)
            db.session.commit()
        except BEMServerCoreCampaignScopeError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries expression"""
        item = TimeseriesExpression.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesExpressionSchema)
        item.delete()
        db.session.commit()
