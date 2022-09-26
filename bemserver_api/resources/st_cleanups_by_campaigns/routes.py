"""ST_CleanupByCampaign resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.scheduled_tasks import ST_CleanupByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    ST_CleanupByCampaignSchema,
    ST_CleanupByCampaignQueryArgsSchema,
    ST_CleanupByCampaignPutSchema,
    ST_CleanupByCampaignFullSchema,
    ST_CleanupByCampaignFullQueryArgsSchema,
)


blp = Blueprint(
    "ST_CleanupByCampaign",
    __name__,
    url_prefix="/st_cleanups_by_campaigns",
    description="Operations on cleanup scheduled task x campaign associations",
)


@blp.route("/")
class ST_CleanupByCampaignViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ST_CleanupByCampaignQueryArgsSchema, location="query")
    @blp.response(200, ST_CleanupByCampaignSchema(many=True))
    def get(self, args):
        """List cleanup scheduled tasks x campaign associations"""
        return ST_CleanupByCampaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(ST_CleanupByCampaignSchema)
    @blp.response(201, ST_CleanupByCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new cleanup scheduled tasks x campaign association"""
        item = ST_CleanupByCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class ST_CleanupByCampaignByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ST_CleanupByCampaignSchema)
    def get(self, item_id):
        """Get cleanup scheduled tasks x campaign association by ID"""
        item = ST_CleanupByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(ST_CleanupByCampaignPutSchema)
    @blp.response(200, ST_CleanupByCampaignSchema)
    def put(self, item_data, item_id):
        """Update cleanup scheduled tasks x campaign association by ID"""
        item = ST_CleanupByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_CleanupByCampaignSchema)
        item.update(**item_data)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a cleanup scheduled tasks x campaign associations"""
        item = ST_CleanupByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_CleanupByCampaignSchema)
        item.delete()
        db.session.commit()


@blp.route("/full")
@blp.login_required
@blp.etag
@blp.arguments(ST_CleanupByCampaignFullQueryArgsSchema, location="query")
@blp.response(200, ST_CleanupByCampaignFullSchema(many=True))
def get_full(args):
    """List cleanup service state for all campaigns"""
    return ST_CleanupByCampaign.get_all(**args)
