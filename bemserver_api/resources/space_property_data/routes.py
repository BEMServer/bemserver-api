"""Space property data resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import SpacePropertyData
from bemserver_core.exceptions import PropertyTypeInvalidError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    SpacePropertyDataSchema,
    SpacePropertyDataQueryArgsSchema,
)


blp = Blueprint(
    "SpacePropertyData",
    __name__,
    url_prefix="/space_property_data",
    description="Operations on space property data",
)


@blp.route("/")
class SpacePropertyDataViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(SpacePropertyDataQueryArgsSchema, location="query")
    @blp.response(200, SpacePropertyDataSchema(many=True))
    def get(self, args):
        """List space property data"""
        return SpacePropertyData.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(SpacePropertyDataSchema)
    @blp.response(201, SpacePropertyDataSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new space property data"""
        item = SpacePropertyData.new(**new_item)
        try:
            db.session.commit()
        except PropertyTypeInvalidError:
            abort(422, errors={"json": {"value": ["Invalid type."]}})
        return item


@blp.route("/<int:item_id>")
class SpacePropertyDataByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, SpacePropertyDataSchema)
    def get(self, item_id):
        """Get space property data by ID"""
        item = SpacePropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(SpacePropertyDataSchema)
    @blp.response(200, SpacePropertyDataSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing space property data"""
        item = SpacePropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, SpacePropertyDataSchema)
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
        """Delete a space property data"""
        item = SpacePropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, SpacePropertyDataSchema)
        item.delete()
        db.session.commit()
