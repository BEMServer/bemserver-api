"""Campaign resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Campaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import CampaignSchema, CampaignQueryArgsSchema


blp = Blueprint(
    "Campaign", __name__, url_prefix="/campaigns", description="Operations on campaigns"
)


@blp.route("/")
class CampaignViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(CampaignQueryArgsSchema, location="query")
    @blp.response(200, CampaignSchema(many=True))
    def get(self, args):
        """List campaigns"""
        return Campaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(CampaignSchema)
    @blp.response(201, CampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new campaign"""
        item = Campaign.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class CampaignByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, CampaignSchema)
    def get(self, item_id):
        """Get campaign by ID"""
        item = Campaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(CampaignSchema)
    @blp.response(200, CampaignSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing campaign"""
        item = Campaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, CampaignSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a campaign"""
        item = Campaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, CampaignSchema)
        item.delete()
        db.session.commit()
