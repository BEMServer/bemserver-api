"""Storey properties resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import StoreyProperty

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    StoreyPropertySchema,
    StoreyPropertyQueryArgsSchema,
)


blp = Blueprint(
    "StoreyProperty",
    __name__,
    url_prefix="/storey_properties",
    description="Operations on storey properties",
)


@blp.route("/")
class StoreyPropertyViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(StoreyPropertyQueryArgsSchema, location="query")
    @blp.response(200, StoreyPropertySchema(many=True))
    def get(self, args):
        """List storey properties"""
        return StoreyProperty.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(StoreyPropertySchema)
    @blp.response(201, StoreyPropertySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new storey property"""
        item = StoreyProperty.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class StoreyPropertyByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, StoreyPropertySchema)
    def get(self, item_id):
        """Get storey property by ID"""
        item = StoreyProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a storey property"""
        item = StoreyProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
