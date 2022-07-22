"""Building property data resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import BuildingPropertyData
from bemserver_core.exceptions import PropertyTypeInvalidError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    BuildingPropertyDataSchema,
    BuildingPropertyDataQueryArgsSchema,
)


blp = Blueprint(
    "BuildingPropertyData",
    __name__,
    url_prefix="/building_property_data",
    description="Operations on building property data",
)


@blp.route("/")
class BuildingPropertyDataViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(BuildingPropertyDataQueryArgsSchema, location="query")
    @blp.response(200, BuildingPropertyDataSchema(many=True))
    def get(self, args):
        """List building property data"""
        return BuildingPropertyData.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(BuildingPropertyDataSchema)
    @blp.response(201, BuildingPropertyDataSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new building property data"""
        item = BuildingPropertyData.new(**new_item)
        try:
            db.session.commit()
        except PropertyTypeInvalidError:
            abort(422, errors={"json": {"value": ["Invalid type."]}})
        return item


@blp.route("/<int:item_id>")
class BuildingPropertyDataByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, BuildingPropertyDataSchema)
    def get(self, item_id):
        """Get building property data by ID"""
        item = BuildingPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(BuildingPropertyDataSchema)
    @blp.response(200, BuildingPropertyDataSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing building property data"""
        item = BuildingPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, BuildingPropertyDataSchema)
        item.update(**new_item)
        try:
            db.session.commit()
        except PropertyTypeInvalidError:
            abort(422, errors={"json": {"value": ["Invalid type."]}})
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a building property data"""
        item = BuildingPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, BuildingPropertyDataSchema)
        item.delete()
        db.session.commit()
