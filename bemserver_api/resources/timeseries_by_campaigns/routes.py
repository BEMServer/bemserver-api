"""Timeseries by campaigns resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

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

    @blp.etag
    @blp.arguments(TimeseriesByCampaignQueryArgsSchema, location='query')
    @blp.response(200, TimeseriesByCampaignSchema(many=True))
    def get(self, args):
        """List campaign x timeseries associations"""
        return db.session.query(TimeseriesByCampaign).filter_by(**args)

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

    @blp.etag
    @blp.response(200, TimeseriesByCampaignSchema)
    def get(self, item_id):
        """Get campaign x timeseries association by ID"""
        item = db.session.get(TimeseriesByCampaign, item_id)
        if item is None:
            abort(404)
        return item

    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a campaign x timeseries association"""
        item = db.session.get(TimeseriesByCampaign, item_id)
        if item is None:
            abort(404)
        db.session.delete(item)
        db.session.commit()
