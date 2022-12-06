"""ST_CheckMissingByCampaign resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.scheduled_tasks import ST_CheckMissingByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    ST_CheckMissingByCampaignSchema,
    ST_CheckMissingByCampaignQueryArgsSchema,
    ST_CheckMissingByCampaignPutSchema,
    ST_CheckMissingByCampaignFullSchema,
    ST_CheckMissingByCampaignFullQueryArgsSchema,
)


blp = Blueprint(
    "ST_CheckMissingByCampaign",
    __name__,
    url_prefix="/st_check_missings_by_campaigns",
    description="Operations on check missings scheduled task x campaign associations",
)


@blp.route("/")
class ST_CheckMissingByCampaignViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ST_CheckMissingByCampaignQueryArgsSchema, location="query")
    @blp.response(200, ST_CheckMissingByCampaignSchema(many=True))
    def get(self, args):
        """List check missings scheduled tasks x campaign associations"""
        return ST_CheckMissingByCampaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(ST_CheckMissingByCampaignSchema)
    @blp.response(201, ST_CheckMissingByCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new check missings scheduled tasks x campaign association"""
        item = ST_CheckMissingByCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class ST_CheckMissingByCampaignByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ST_CheckMissingByCampaignSchema)
    def get(self, item_id):
        """Get check missings scheduled tasks x campaign association by ID"""
        item = ST_CheckMissingByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(ST_CheckMissingByCampaignPutSchema)
    @blp.response(200, ST_CheckMissingByCampaignSchema)
    def put(self, item_data, item_id):
        """Update check missings scheduled tasks x campaign association by ID"""
        item = ST_CheckMissingByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_CheckMissingByCampaignSchema)
        item.update(**item_data)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a check missings scheduled tasks x campaign associations"""
        item = ST_CheckMissingByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_CheckMissingByCampaignSchema)
        item.delete()
        db.session.commit()


@blp.route("/full")
@blp.login_required
@blp.etag
@blp.arguments(ST_CheckMissingByCampaignFullQueryArgsSchema, location="query")
@blp.response(200, ST_CheckMissingByCampaignFullSchema(many=True))
def get_full(args):
    """List check missings service state for all campaigns"""
    return ST_CheckMissingByCampaign.get_all(**args)
