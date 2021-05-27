"""Timeseries by campaigns resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesByCampaignByUser

from bemserver_api import Blueprint
from bemserver_api.database import db

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
class TimeseriesByCampaignViews(MethodView):

    @blp.etag
    @blp.arguments(TimeseriesByCampaignByUserQueryArgsSchema, location='query')
    @blp.response(200, TimeseriesByCampaignByUserSchema(many=True))
    def get(self, args):
        """List campaign x timeseries x users associations"""
        return db.session.query(TimeseriesByCampaignByUser).filter_by(**args)

    @blp.etag
    @blp.arguments(TimeseriesByCampaignByUserSchema)
    @blp.response(201, TimeseriesByCampaignByUserSchema)
    def post(self, new_item):
        """Add a new campaign x timeseries x user association"""
        item = TimeseriesByCampaignByUser(**new_item)
        db.session.add(item)
        db.session.commit()
        return item


@blp.route('/<int:item_id>')
class TimeseriesByCampaignByIdViews(MethodView):

    @blp.etag
    @blp.response(200, TimeseriesByCampaignByUserSchema)
    def get(self, item_id):
        """Get campaign x timeseries x users association by ID"""
        item = db.session.get(TimeseriesByCampaignByUser, item_id)
        if item is None:
            abort(404)
        return item

    @blp.response(204)
    def delete(self, item_id):
        """Delete a campaign x timeseries x user association"""
        item = db.session.get(TimeseriesByCampaignByUser, item_id)
        if item is None:
            abort(404)
        db.session.delete(item)
        db.session.commit()
