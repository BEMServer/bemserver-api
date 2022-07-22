"""Building properties resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import BuildingProperty

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    BuildingPropertySchema,
    BuildingPropertyQueryArgsSchema,
)


blp = Blueprint(
    "BuildingProperty",
    __name__,
    url_prefix="/building_properties",
    description="Operations on building properties",
)


@blp.route("/")
class BuildingPropertyViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(BuildingPropertyQueryArgsSchema, location="query")
    @blp.response(200, BuildingPropertySchema(many=True))
    def get(self, args):
        """List building properties"""
        return BuildingProperty.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(BuildingPropertySchema)
    @blp.response(201, BuildingPropertySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new building property"""
        item = BuildingProperty.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class BuildingPropertyByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, BuildingPropertySchema)
    def get(self, item_id):
        """Get building property by ID"""
        item = BuildingProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a building property"""
        item = BuildingProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
