"""Site properties resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import SiteProperty

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    SitePropertySchema,
    SitePropertyQueryArgsSchema,
)


blp = Blueprint(
    "SiteProperty",
    __name__,
    url_prefix="/site_properties",
    description="Operations on site properties",
)


@blp.route("/")
class SitePropertyViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(SitePropertyQueryArgsSchema, location="query")
    @blp.response(200, SitePropertySchema(many=True))
    def get(self, args):
        """List site properties"""
        return SiteProperty.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(SitePropertySchema)
    @blp.response(201, SitePropertySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new site property"""
        item = SiteProperty.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class SitePropertyByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, SitePropertySchema)
    def get(self, item_id):
        """Get site property by ID"""
        item = SiteProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a site property"""
        item = SiteProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
