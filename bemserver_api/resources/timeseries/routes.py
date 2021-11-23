"""Timeseries resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Timeseries

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db
from bemserver_api.resources.campaigns import blp as campaigns_blp

from .schemas import (
    TimeseriesSchema, TimeseriesQueryArgsSchema, TimeseriesByIdQueryArgsSchema
)

blp = Blueprint(
    'Timeseries',
    __name__,
    url_prefix='/timeseries',
    description="Operations on timeseries"
)


@blp.route('/')
class TimeseriesViews(MethodView):

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesQueryArgsSchema, location='query')
    @blp.response(200, TimeseriesSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List timeseries"""
        return Timeseries.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesSchema)
    @blp.response(201, TimeseriesSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries"""
        item = Timeseries.new(**new_item)
        db.session.commit()
        return item


@blp.route('/<int:item_id>')
class TimeseriesByIdViews(MethodView):

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesByIdQueryArgsSchema, location='query')
    @blp.response(200, TimeseriesSchema)
    def get(self, args, item_id):
        """Get timeseries by ID"""
        item = Timeseries.get_by_id(item_id, **args)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesSchema)
    @blp.response(200, TimeseriesSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries"""
        item = Timeseries.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a timeseries"""
        item = Timeseries.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesSchema)
        item.delete()
        db.session.commit()


@campaigns_blp.route('/<int:campaign_id>/timeseries/')
class TimeseriesForCampaignViews(MethodView):

    @campaigns_blp.login_required
    @campaigns_blp.etag
    @campaigns_blp.arguments(
        TimeseriesQueryArgsSchema(exclude=("campaign_id", )),
        location='query'
    )
    @campaigns_blp.response(200, TimeseriesSchema(many=True))
    @campaigns_blp.paginate(SQLCursorPage)
    def get(self, args, campaign_id):
        """List timeseries for campaign"""
        return Timeseries.get(campaign_id=campaign_id, **args)


@campaigns_blp.route('/<int:campaign_id>/timeseries/<int:item_id>')
class TimeseriesForCampaignByIdViews(MethodView):

    @campaigns_blp.login_required
    @campaigns_blp.etag
    @campaigns_blp.response(200, TimeseriesSchema)
    def get(self, campaign_id, item_id):
        """Get timeseries by ID for campaign"""
        item = Timeseries.get_by_id(item_id, campaign_id=campaign_id)
        if item is None:
            abort(404)
        return item
