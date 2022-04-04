"""User groups resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import UserGroup

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import UserGroupSchema, UserGroupQueryArgsSchema


blp = Blueprint(
    "UserGroup",
    __name__,
    url_prefix="/user_groups",
    description="Operations on users groups",
)


@blp.route("/")
class UserGroupViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(UserGroupQueryArgsSchema, location="query")
    @blp.response(200, UserGroupSchema(many=True))
    def get(self, args):
        """List user groups"""
        return UserGroup.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(UserGroupSchema)
    @blp.response(201, UserGroupSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new user group"""
        item = UserGroup.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class UserGroupByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, UserGroupSchema)
    def get(self, item_id):
        """Get user group by ID"""
        item = UserGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(UserGroupSchema)
    @blp.response(200, UserGroupSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing user group"""
        item = UserGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, UserGroupSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a user group"""
        item = UserGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, UserGroupSchema)
        item.delete()
        db.session.commit()
