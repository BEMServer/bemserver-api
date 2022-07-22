"""Space properties resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import SpaceProperty

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    SpacePropertySchema,
    SpacePropertyQueryArgsSchema,
)


blp = Blueprint(
    "SpaceProperty",
    __name__,
    url_prefix="/space_properties",
    description="Operations on space properties",
)


@blp.route("/")
class SpacePropertyViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(SpacePropertyQueryArgsSchema, location="query")
    @blp.response(200, SpacePropertySchema(many=True))
    def get(self, args):
        """List space properties"""
        return SpaceProperty.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(SpacePropertySchema)
    @blp.response(201, SpacePropertySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new space property"""
        item = SpaceProperty.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class SpacePropertyByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, SpacePropertySchema)
    def get(self, item_id):
        """Get space property by ID"""
        item = SpaceProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a space property"""
        item = SpaceProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
