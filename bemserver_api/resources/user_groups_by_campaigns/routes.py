"""User groups by campaigns resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import UserGroupByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import UserGroupByCampaignSchema, UserGroupByCampaignQueryArgsSchema


blp = Blueprint(
    "UserGroupByCampaign",
    __name__,
    url_prefix="/user_groups_by_campaigns",
    description="Operations on user group x campaign associations",
)


@blp.route("/")
class UserGroupByCampaignViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(UserGroupByCampaignQueryArgsSchema, location="query")
    @blp.response(200, UserGroupByCampaignSchema(many=True))
    def get(self, args):
        """List user group x campaign associations"""
        return UserGroupByCampaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(UserGroupByCampaignSchema)
    @blp.response(201, UserGroupByCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new user group x campaign association"""
        item = UserGroupByCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class UserGroupByCampaignByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, UserGroupByCampaignSchema)
    def get(self, item_id):
        """Get user group x campaign association by ID"""
        item = UserGroupByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a user group x campaign association"""
        item = UserGroupByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
