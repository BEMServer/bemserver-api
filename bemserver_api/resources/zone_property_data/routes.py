"""Zone property data resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import ZonePropertyData
from bemserver_core.exceptions import PropertyTypeInvalidError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    ZonePropertyDataSchema,
    ZonePropertyDataQueryArgsSchema,
)


blp = Blueprint(
    "ZonePropertyData",
    __name__,
    url_prefix="/zone_property_data",
    description="Operations on zone property data",
)


@blp.route("/")
class ZonePropertyDataViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ZonePropertyDataQueryArgsSchema, location="query")
    @blp.response(200, ZonePropertyDataSchema(many=True))
    def get(self, args):
        """List zone property data"""
        return ZonePropertyData.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(ZonePropertyDataSchema)
    @blp.response(201, ZonePropertyDataSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new zone property data"""
        item = ZonePropertyData.new(**new_item)
        try:
            db.session.commit()
        except PropertyTypeInvalidError:
            abort(422, message="Invalid value type")
        return item


@blp.route("/<int:item_id>")
class ZonePropertyDataByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ZonePropertyDataSchema)
    def get(self, item_id):
        """Get zone property data by ID"""
        item = ZonePropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(ZonePropertyDataSchema)
    @blp.response(200, ZonePropertyDataSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing zone property data"""
        item = ZonePropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ZonePropertyDataSchema)
        item.update(**new_item)
        try:
            db.session.commit()
        except PropertyTypeInvalidError:
            abort(422, message="Invalid value type")
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a zone property data"""
        item = ZonePropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ZonePropertyDataSchema)
        item.delete()
        db.session.commit()
