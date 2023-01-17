"""ST_CheckOutliersByCampaign resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.scheduled_tasks import ST_CheckOutliersByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    ST_CheckOutliersByCampaignSchema,
    ST_CheckOutliersByCampaignQueryArgsSchema,
    ST_CheckOutliersByCampaignPutSchema,
    ST_CheckOutliersByCampaignFullSchema,
    ST_CheckOutliersByCampaignFullQueryArgsSchema,
)


blp = Blueprint(
    "ST_CheckOutliersByCampaign",
    __name__,
    url_prefix="/st_check_outliers_by_campaigns",
    description="Operations on check outliers scheduled task x campaign associations",
)


@blp.route("/")
class ST_CheckOutliersByCampaignViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ST_CheckOutliersByCampaignQueryArgsSchema, location="query")
    @blp.response(200, ST_CheckOutliersByCampaignSchema(many=True))
    def get(self, args):
        """List check outliers scheduled tasks x campaign associations"""
        return ST_CheckOutliersByCampaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(ST_CheckOutliersByCampaignSchema)
    @blp.response(201, ST_CheckOutliersByCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new check outliers scheduled tasks x campaign association"""
        item = ST_CheckOutliersByCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class ST_CheckOutliersByCampaignByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ST_CheckOutliersByCampaignSchema)
    def get(self, item_id):
        """Get check outliers scheduled tasks x campaign association by ID"""
        item = ST_CheckOutliersByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(ST_CheckOutliersByCampaignPutSchema)
    @blp.response(200, ST_CheckOutliersByCampaignSchema)
    def put(self, item_data, item_id):
        """Update check outliers scheduled tasks x campaign association by ID"""
        item = ST_CheckOutliersByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_CheckOutliersByCampaignSchema)
        item.update(**item_data)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a check outliers scheduled tasks x campaign associations"""
        item = ST_CheckOutliersByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ST_CheckOutliersByCampaignSchema)
        item.delete()
        db.session.commit()


@blp.route("/full")
@blp.login_required
@blp.etag
@blp.arguments(ST_CheckOutliersByCampaignFullQueryArgsSchema, location="query")
@blp.response(200, ST_CheckOutliersByCampaignFullSchema(many=True))
def get_full(args):
    """List check outliers service state for all campaigns"""
    return ST_CheckOutliersByCampaign.get_all(**args)
