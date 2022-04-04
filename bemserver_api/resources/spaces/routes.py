"""Space resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Space

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import SpaceSchema, SpacePutSchema, SpaceQueryArgsSchema


blp = Blueprint(
    "Space", __name__, url_prefix="/spaces", description="Operations on spaces"
)


@blp.route("/")
class SpaceViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(SpaceQueryArgsSchema, location="query")
    @blp.response(200, SpaceSchema(many=True))
    def get(self, args):
        """List spaces"""
        return Space.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(SpaceSchema)
    @blp.response(201, SpaceSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new space"""
        item = Space.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class SpaceByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, SpaceSchema)
    def get(self, item_id):
        """Get space by ID"""
        item = Space.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(SpacePutSchema)
    @blp.response(200, SpaceSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing space"""
        item = Space.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, SpaceSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a space"""
        item = Space.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, SpaceSchema)
        item.delete()
        db.session.commit()
