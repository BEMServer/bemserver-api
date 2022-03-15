"""User groups by campaign scopes resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import UserGroupByCampaignScope

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    UserGroupByCampaignScopeSchema,
    UserGroupByCampaignScopeQueryArgsSchema,
)


blp = Blueprint(
    "UserGroupByCampaignScope",
    __name__,
    url_prefix="/user_groups_by_campaign_scopes",
    description="Operations on user group x campaign scope associations",
)


@blp.route("/")
class UserGroupByCampaignScopeViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(UserGroupByCampaignScopeQueryArgsSchema, location="query")
    @blp.response(200, UserGroupByCampaignScopeSchema(many=True))
    def get(self, args):
        """List user group x campaign scope associations"""
        return UserGroupByCampaignScope.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(UserGroupByCampaignScopeSchema)
    @blp.response(201, UserGroupByCampaignScopeSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new user group x campaign scope association"""
        item = UserGroupByCampaignScope.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class UserGroupByCampaignScopeByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, UserGroupByCampaignScopeSchema)
    def get(self, item_id):
        """Get user group x campaign scope association by ID"""
        item = UserGroupByCampaignScope.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a user group x campaign scope association"""
        item = UserGroupByCampaignScope.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
