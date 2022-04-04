"""Campaign scopes resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import CampaignScope

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    CampaignScopeSchema,
    CampaignScopePutSchema,
    CampaignScopeQueryArgsSchema,
)


blp = Blueprint(
    "CampaignScope",
    __name__,
    url_prefix="/campaign_scopes",
    description="Operations on campaign scopes",
)


@blp.route("/")
class CampaignScopeViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(CampaignScopeQueryArgsSchema, location="query")
    @blp.response(200, CampaignScopeSchema(many=True))
    def get(self, args):
        """List campaign scopes"""
        return CampaignScope.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(CampaignScopeSchema)
    @blp.response(201, CampaignScopeSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new campaign scope"""
        item = CampaignScope.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class CampaignScopeByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, CampaignScopeSchema)
    def get(self, item_id):
        """Get campaign scope by ID"""
        item = CampaignScope.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(CampaignScopePutSchema)
    @blp.response(200, CampaignScopeSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing campaign scope"""
        item = CampaignScope.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, CampaignScopeSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a campaign scope"""
        item = CampaignScope.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, CampaignScopeSchema)
        item.delete()
        db.session.commit()
