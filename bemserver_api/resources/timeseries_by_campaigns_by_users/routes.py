"""Timeseries by campaigns by users resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesByCampaignByUser

from bemserver_api import Blueprint
from bemserver_api.database import db
from bemserver_api.resources.campaigns import blp as campaigns_blp

from .schemas import (
    TimeseriesByCampaignByUserSchema,
    TimeseriesByCampaignByUserQueryArgsSchema
)


blp = Blueprint(
    'TimeseriesByCampaignByUser',
    __name__,
    url_prefix='/timeseriesbycampaignsbyusers',
    description="Operations on timeseries x campaigns x users associations"
)


@blp.route('/')
class TimeseriesByCampaignByUserViews(MethodView):

    @blp.login_required(role=["admin"])
    @blp.etag
    @blp.arguments(TimeseriesByCampaignByUserQueryArgsSchema, location='query')
    @blp.response(200, TimeseriesByCampaignByUserSchema(many=True))
    def get(self, args):
        """List campaign x timeseries x users associations"""
        return TimeseriesByCampaignByUser.get(**args)

    @blp.login_required(role=["admin"])
    @blp.etag
    @blp.arguments(TimeseriesByCampaignByUserSchema)
    @blp.response(201, TimeseriesByCampaignByUserSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new campaign x timeseries x user association"""
        item = TimeseriesByCampaignByUser.new(**new_item)
        db.session.commit()
        return item


@blp.route('/<int:item_id>')
class TimeseriesByCampaignByUserByIdViews(MethodView):

    @blp.login_required(role=["admin"])
    @blp.etag
    @blp.response(200, TimeseriesByCampaignByUserSchema)
    def get(self, item_id):
        """Get campaign x timeseries x users association by ID"""
        item = TimeseriesByCampaignByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required(role=["admin"])
    @blp.response(204)
    def delete(self, item_id):
        """Delete a campaign x timeseries x user association"""
        item = TimeseriesByCampaignByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()


@campaigns_blp.route('/<int:campaign_id>/timeseriesbycampaignsbyusers/')
class TimeseriesByCampaignByUserForCampaignViews(MethodView):

    @campaigns_blp.login_required(role=["admin", "user"])
    @campaigns_blp.etag
    @campaigns_blp.arguments(
        TimeseriesByCampaignByUserQueryArgsSchema,
        location='query'
    )
    @campaigns_blp.response(200, TimeseriesByCampaignByUserSchema(many=True))
    def get(self, args, campaign_id):
        """List campaign x timeseries associations for campaign"""
        return TimeseriesByCampaignByUser.get(campaign_id=campaign_id, **args)


@campaigns_blp.route(
    '/<int:campaign_id>/timeseriesbycampaignsbyusers/<int:item_id>')
class TimeseriesByCampaignByUserForCampaignByIdViews(MethodView):

    @campaigns_blp.login_required(role=["admin", "user"])
    @campaigns_blp.etag
    @campaigns_blp.response(200, TimeseriesByCampaignByUserSchema)
    def get(self, campaign_id, item_id):
        """Get campaign x timeseries association by ID for campaign"""
        item = TimeseriesByCampaignByUser.get_by_id(
            item_id, campaign_id=campaign_id)
        if item is None:
            abort(404)
        return item
