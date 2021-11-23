"""Timeseries by campaigns resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db
from bemserver_api.resources.campaigns import blp as campaigns_blp

from .schemas import (
    TimeseriesByCampaignSchema,
    TimeseriesByCampaignQueryArgsSchema
)


blp = Blueprint(
    'TimeseriesByCampaign',
    __name__,
    url_prefix='/timeseriesbycampaigns',
    description="Operations on timeseries x campaigns associations"
)


@blp.route('/')
class TimeseriesByCampaignViews(MethodView):

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesByCampaignQueryArgsSchema, location='query')
    @blp.response(200, TimeseriesByCampaignSchema(many=True))
    def get(self, args):
        """List campaign x timeseries associations"""
        return TimeseriesByCampaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesByCampaignSchema)
    @blp.response(201, TimeseriesByCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new campaign x timeseries association"""
        item = TimeseriesByCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route('/<int:item_id>')
class TimeseriesByCampaignByIdViews(MethodView):

    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesByCampaignSchema)
    def get(self, item_id):
        """Get campaign x timeseries association by ID"""
        item = TimeseriesByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a campaign x timeseries association"""
        item = TimeseriesByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()


@campaigns_blp.route('/<int:campaign_id>/timeseriesbycampaigns/')
class TimeseriesByCampaignForCampaignViews(MethodView):

    @campaigns_blp.login_required
    @campaigns_blp.etag
    @campaigns_blp.arguments(
        TimeseriesByCampaignQueryArgsSchema(exclude=("campaign_id", )),
        location='query'
    )
    @campaigns_blp.response(200, TimeseriesByCampaignSchema(many=True))
    def get(self, args, campaign_id):
        """List campaign x timeseries associations for campaign"""
        return TimeseriesByCampaign.get(campaign_id=campaign_id, **args)


@campaigns_blp.route('/<int:campaign_id>/timeseriesbycampaigns/<int:item_id>')
class TimeseriesByCampaignForCampaignByIdViews(MethodView):

    @campaigns_blp.login_required
    @campaigns_blp.etag
    @campaigns_blp.response(200, TimeseriesByCampaignSchema)
    def get(self, campaign_id, item_id):
        """Get campaign x timeseries association by ID for campaign"""
        item = TimeseriesByCampaign.get_by_id(item_id, campaign_id=campaign_id)
        if item is None:
            abort(404)
        return item
