"""TimeseriesEvents resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Campaign, TimeseriesEvent
from bemserver_core.authorization import CurrentCampaign

from bemserver_api import SQLCursorPage
from bemserver_api.database import db
from bemserver_api.resources.campaigns import blp as campaigns_blp

from .schemas import (
    TimeseriesEventSchema, TimeseriesEventPutSchema,
    TimeseriesEventQueryArgsSchema,
)


@campaigns_blp.route('/<int:campaign_id>/events/timeseries/')
class TimeseriesEventsViews(MethodView):

    @campaigns_blp.login_required
    @campaigns_blp.etag
    @campaigns_blp.arguments(TimeseriesEventQueryArgsSchema, location='query')
    @campaigns_blp.response(200, TimeseriesEventSchema(many=True))
    @campaigns_blp.paginate(SQLCursorPage)
    # TODO: kwargs?
    def get(self, args, campaign_id):
        """List events"""
        campaign = Campaign.get_by_id(campaign_id)
        if campaign is None:
            abort(404)
        with CurrentCampaign(campaign):
            return TimeseriesEvent.get(**args)

    @campaigns_blp.login_required
    @campaigns_blp.etag
    @campaigns_blp.arguments(TimeseriesEventSchema)
    @campaigns_blp.response(201, TimeseriesEventSchema)
    @campaigns_blp.catch_integrity_error
    def post(self, new_item, campaign_id):
        """Add a new event"""
        campaign = Campaign.get_by_id(campaign_id)
        if campaign is None:
            abort(404)
        with CurrentCampaign(campaign):
            item = TimeseriesEvent.new(**new_item)
            db.session.commit()
            return item


@campaigns_blp.route('/<int:campaign_id>/events/timeseries/<int:item_id>')
class TimeseriesEventsByIdViews(MethodView):

    @campaigns_blp.login_required
    @campaigns_blp.etag
    @campaigns_blp.response(200, TimeseriesEventSchema)
    def get(self, item_id, campaign_id):
        """Get en event by its ID"""
        campaign = Campaign.get_by_id(campaign_id)
        if campaign is None:
            abort(404)
        with CurrentCampaign(campaign):
            item = TimeseriesEvent.get_by_id(item_id)
            if item is None:
                abort(404)
            return item

    @campaigns_blp.login_required
    @campaigns_blp.etag
    @campaigns_blp.arguments(TimeseriesEventPutSchema)
    @campaigns_blp.response(200, TimeseriesEventSchema)
    @campaigns_blp.catch_integrity_error
    def put(self, new_item, item_id, campaign_id):
        """Update an existing timeseries"""
        campaign = Campaign.get_by_id(campaign_id)
        if campaign is None:
            abort(404)
        with CurrentCampaign(campaign):
            item = TimeseriesEvent.get_by_id(item_id)
            if item is None:
                abort(404)
            campaigns_blp.check_etag(item, TimeseriesEventSchema)
            item.update(**new_item)
            db.session.commit()
            return item

    @campaigns_blp.login_required
    @campaigns_blp.etag
    @campaigns_blp.response(204)
    def delete(self, item_id, campaign_id):
        """Delete an event"""
        campaign = Campaign.get_by_id(campaign_id)
        if campaign is None:
            abort(404)
        with CurrentCampaign(campaign):
            item = TimeseriesEvent.get_by_id(item_id)
            if item is None:
                abort(404)
            campaigns_blp.check_etag(item, TimeseriesEventSchema)
            item.delete()
            db.session.commit()
