"""Building resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Building

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import BuildingSchema, BuildingPutSchema, BuildingQueryArgsSchema


blp = Blueprint(
    "Building", __name__, url_prefix="/buildings", description="Operations on buildings"
)


@blp.route("/")
class BuildingViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(BuildingQueryArgsSchema, location="query")
    @blp.response(200, BuildingSchema(many=True))
    def get(self, args):
        """List buildings"""
        return Building.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(BuildingSchema)
    @blp.response(201, BuildingSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new building"""
        item = Building.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class BuildingByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, BuildingSchema)
    def get(self, item_id):
        """Get building by ID"""
        item = Building.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(BuildingPutSchema)
    @blp.response(200, BuildingSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing building"""
        item = Building.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, BuildingSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a building"""
        item = Building.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, BuildingSchema)
        item.delete()
        db.session.commit()
