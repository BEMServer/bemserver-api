"""Storey property data resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import StoreyPropertyData

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    StoreyPropertyDataSchema,
    StoreyPropertyDataQueryArgsSchema,
)


blp = Blueprint(
    "Storey property data",
    __name__,
    url_prefix="/storey_property_data",
    description="Operations on storey property data",
)


@blp.route("/")
class StructuralElementPropertiesViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(StoreyPropertyDataQueryArgsSchema, location="query")
    @blp.response(200, StoreyPropertyDataSchema(many=True))
    def get(self, args):
        """List storey property data"""
        return StoreyPropertyData.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(StoreyPropertyDataSchema)
    @blp.response(201, StoreyPropertyDataSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new storey property data"""
        item = StoreyPropertyData.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class StoreyPropertyDataByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, StoreyPropertyDataSchema)
    def get(self, item_id):
        """Get storey property data by ID"""
        item = StoreyPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(StoreyPropertyDataSchema)
    @blp.response(200, StoreyPropertyDataSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Get an exsiting storey property data by ID"""
        item = StoreyPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, StoreyPropertyDataSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a storey property data"""
        item = StoreyPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, StoreyPropertyDataSchema)
        item.delete()
        db.session.commit()