"""Zone properties resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import ZoneProperty

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    ZonePropertySchema,
    ZonePropertyQueryArgsSchema,
)


blp = Blueprint(
    "Zone properties",
    __name__,
    url_prefix="/zone_properties",
    description="Operations on zone properties",
)


@blp.route("/")
class StructuralElementPropertiesViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ZonePropertyQueryArgsSchema, location="query")
    @blp.response(200, ZonePropertySchema(many=True))
    def get(self, args):
        """List zone properties"""
        return ZoneProperty.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(ZonePropertySchema)
    @blp.response(201, ZonePropertySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new zone property"""
        item = ZoneProperty.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class ZonePropertyByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ZonePropertySchema)
    def get(self, item_id):
        """Get zone property by ID"""
        item = ZoneProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a zone property"""
        item = ZoneProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ZonePropertySchema)
        item.delete()
        db.session.commit()