"""Expressions resources"""

from flask.views import MethodView

from flask_smorest import abort

from bemserver_core.exceptions import BEMServerCoreCampaignScopeError
from bemserver_core.model import Expression

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import ExpressionPutSchema, ExpressionQueryArgsSchema, ExpressionSchema

blp = Blueprint(
    "Expression",
    __name__,
    url_prefix="/expressions",
    description="Operations on expressions",
)


@blp.route("/")
class ExpressionViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ExpressionQueryArgsSchema, location="query")
    @blp.response(200, ExpressionSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List expressions"""
        return Expression.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(ExpressionSchema)
    @blp.response(201, ExpressionSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new expression"""
        item = Expression.new(**new_item)
        try:
            db.session.commit()
        except BEMServerCoreCampaignScopeError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item


@blp.route("/<int:item_id>")
class ExpressionByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ExpressionSchema)
    def get(self, item_id):
        """Get expression by ID"""
        item = Expression.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(ExpressionPutSchema)
    @blp.response(200, ExpressionSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing expression"""
        item = Expression.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ExpressionSchema)
        item.update(**new_item)
        try:
            db.session.commit()
        except BEMServerCoreCampaignScopeError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete an expression"""
        item = Expression.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ExpressionSchema)
        item.delete()
        db.session.commit()
