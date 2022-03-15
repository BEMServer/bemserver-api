"""Users by user groups resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import UserByUserGroup

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import UserByUserGroupSchema, UserByUserGroupQueryArgsSchema


blp = Blueprint(
    "UserByUserGroup",
    __name__,
    url_prefix="/users_by_user_groups",
    description="Operations on users x user groups associations",
)


@blp.route("/")
class UserByUserGroupViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(UserByUserGroupQueryArgsSchema, location="query")
    @blp.response(200, UserByUserGroupSchema(many=True))
    def get(self, args):
        """List user x user group associations"""
        return UserByUserGroup.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(UserByUserGroupSchema)
    @blp.response(201, UserByUserGroupSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new user x user group association"""
        item = UserByUserGroup.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class UserByUserGroupByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, UserByUserGroupSchema)
    def get(self, item_id):
        """Get user x user group association by ID"""
        item = UserByUserGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a user x user group association"""
        item = UserByUserGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
