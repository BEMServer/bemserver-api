"""Structural element properties resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import StructuralElementProperty

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    StructuralElementPropertySchema,
    StructuralElementPropertyPutSchema,
    StructuralElementPropertyQueryArgsSchema,
)


blp = Blueprint(
    "StructuralElementProperty",
    __name__,
    url_prefix="/structural_element_properties",
    description="Operations on structural element properties",
)


@blp.route("/")
class StructuralElementPropertiesViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(StructuralElementPropertyQueryArgsSchema, location="query")
    @blp.response(200, StructuralElementPropertySchema(many=True))
    def get(self, args):
        """List structural element properties"""
        return StructuralElementProperty.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(StructuralElementPropertySchema)
    @blp.response(201, StructuralElementPropertySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new structural element property"""
        item = StructuralElementProperty.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class StructuralElementPropertyByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, StructuralElementPropertySchema)
    def get(self, item_id):
        """Get structural element property by ID"""
        item = StructuralElementProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(StructuralElementPropertyPutSchema)
    @blp.response(200, StructuralElementPropertySchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing structural element property"""
        item = StructuralElementProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, StructuralElementPropertySchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a structural element property"""
        item = StructuralElementProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, StructuralElementPropertySchema)
        item.delete()
        db.session.commit()
