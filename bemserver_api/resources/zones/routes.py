"""Zone resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Zone

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import ZoneSchema, ZonePutSchema, ZoneQueryArgsSchema


blp = Blueprint(
    "Zone", __name__, url_prefix="/zones", description="Operations on zones"
)


@blp.route("/")
class ZoneViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ZoneQueryArgsSchema, location="query")
    @blp.response(200, ZoneSchema(many=True))
    def get(self, args):
        """List zones"""
        return Zone.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(ZoneSchema)
    @blp.response(201, ZoneSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new zone"""
        item = Zone.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class ZoneByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ZoneSchema)
    def get(self, item_id):
        """Get zone by ID"""
        item = Zone.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(ZonePutSchema)
    @blp.response(200, ZoneSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing zone"""
        item = Zone.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ZoneSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a zone"""
        item = Zone.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ZoneSchema)
        item.delete()
        db.session.commit()
