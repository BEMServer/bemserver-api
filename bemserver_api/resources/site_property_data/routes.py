"""Site property data resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import SitePropertyData
from bemserver_core.exceptions import PropertyTypeInvalidError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    SitePropertyDataSchema,
    SitePropertyDataQueryArgsSchema,
)


blp = Blueprint(
    "SitePropertyData",
    __name__,
    url_prefix="/site_property_data",
    description="Operations on site property data",
)


@blp.route("/")
class SitePropertyDataViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(SitePropertyDataQueryArgsSchema, location="query")
    @blp.response(200, SitePropertyDataSchema(many=True))
    def get(self, args):
        """List site property data"""
        return SitePropertyData.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(SitePropertyDataSchema)
    @blp.response(201, SitePropertyDataSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new site property data"""
        item = SitePropertyData.new(**new_item)
        try:
            db.session.commit()
        except PropertyTypeInvalidError:
            abort(422, errors={"json": {"value": ["Invalid type."]}})
        return item


@blp.route("/<int:item_id>")
class SitePropertyDataByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, SitePropertyDataSchema)
    def get(self, item_id):
        """Get site property data by ID"""
        item = SitePropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(SitePropertyDataSchema)
    @blp.response(200, SitePropertyDataSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing site property data"""
        item = SitePropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, SitePropertyDataSchema)
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
        """Delete a site property data"""
        item = SitePropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, SitePropertyDataSchema)
        item.delete()
        db.session.commit()
