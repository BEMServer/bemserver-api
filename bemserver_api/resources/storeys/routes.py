"""Storey resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Storey

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import StoreySchema, StoreyPutSchema, StoreyQueryArgsSchema


blp = Blueprint(
    "Storey", __name__, url_prefix="/storeys", description="Operations on storeys"
)


@blp.route("/")
class StoreyViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(StoreyQueryArgsSchema, location="query")
    @blp.response(200, StoreySchema(many=True))
    def get(self, args):
        """List storeys"""
        return Storey.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(StoreySchema)
    @blp.response(201, StoreySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new storey"""
        item = Storey.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class StoreyByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, StoreySchema)
    def get(self, item_id):
        """Get storey by ID"""
        item = Storey.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(StoreyPutSchema)
    @blp.response(200, StoreySchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing storey"""
        item = Storey.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, StoreySchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a storey"""
        item = Storey.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, StoreySchema)
        item.delete()
        db.session.commit()
