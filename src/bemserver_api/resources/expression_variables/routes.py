"""Expression variables resources"""

from flask.views import MethodView

from flask_smorest import abort

from bemserver_core.exceptions import BEMServerCoreCampaignScopeError
from bemserver_core.model import ExpressionVariable

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    ExpressionVariablePutSchema,
    ExpressionVariableQueryArgsSchema,
    ExpressionVariableSchema,
)

blp = Blueprint(
    "ExpressionVariable",
    __name__,
    url_prefix="/expression_variables",
    description="Operations on expression variables",
)


@blp.route("/")
class ExpressionVariableViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(ExpressionVariableQueryArgsSchema, location="query")
    @blp.response(200, ExpressionVariableSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List expression variables"""
        return ExpressionVariable.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(ExpressionVariableSchema)
    @blp.response(201, ExpressionVariableSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new expression variable"""
        item = ExpressionVariable.new(**new_item)
        try:
            db.session.commit()
        except BEMServerCoreCampaignScopeError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item


@blp.route("/<int:item_id>")
class ExpressionVariableByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, ExpressionVariableSchema)
    def get(self, item_id):
        """Get expression variable by ID"""
        item = ExpressionVariable.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(ExpressionVariablePutSchema)
    @blp.response(200, ExpressionVariableSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing expression variable"""
        item = ExpressionVariable.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ExpressionVariableSchema)
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
        """Delete an expression variable"""
        item = ExpressionVariable.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, ExpressionVariableSchema)
        item.delete()
        db.session.commit()
