"""Expressions resources"""

from flask.views import MethodView

from flask_smorest import abort

import numpy as np
import pandas as pd

from bemserver_core.exceptions import (
    BEMServerCoreCampaignScopeError,
    BEMServerCoreExpressionValidationError,
)
from bemserver_core.model import Expression, TimeseriesDataState
from bemserver_core.processing.expressions import evaluate, evaluate_from_dict

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    ExpressionEvaluateQueryArgsSchema,
    ExpressionEvaluateSchema,
    ExpressionPutSchema,
    ExpressionQueryArgsSchema,
    ExpressionSchema,
)

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
        item = Expression.from_dict(new_item)
        try:
            item.validate()
        except (
            BEMServerCoreExpressionValidationError,
            BEMServerCoreCampaignScopeError,
        ) as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
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
        try:
            item.update_from_dict(new_item)
        except BEMServerCoreCampaignScopeError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        try:
            item.validate()
        except BEMServerCoreExpressionValidationError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
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


@blp.route("/<int:item_id>/evaluate", methods=("GET",))
@blp.login_required
@blp.arguments(ExpressionEvaluateQueryArgsSchema, location="query")
@blp.response(200, content_type="application/json")
def evaluate_expression_by_id(query_args, item_id):
    """Evaluate an expression"""
    expression = Expression.get_by_id(item_id)
    if expression is None:
        abort(404)

    data_state = TimeseriesDataState.get_by_id(query_args["data_state"]) or abort(
        422, errors={"query": {"data_state": "Unknown data state ID"}}
    )

    data_s = evaluate(
        expression,
        query_args["start_time"],
        query_args["end_time"],
        data_state,
        query_args["bucket_width_value"],
        query_args["bucket_width_unit"],
        query_args["timezone"],
    )

    data_s = data_s.dropna().replace(np.nan, None)
    data_s.index = pd.Series(data_s.index).apply(lambda x: x.isoformat())

    return data_s.to_dict()


@blp.route("/evaluate", methods=("POST",))
@blp.login_required
@blp.arguments(ExpressionEvaluateSchema)
@blp.arguments(ExpressionEvaluateQueryArgsSchema, location="query")
@blp.response(200, content_type="application/json")
def evaluate_expression_from_dict(expression, query_args):
    """Evaluate an expression provided in request body"""
    data_state = TimeseriesDataState.get_by_id(query_args["data_state"]) or abort(
        422, errors={"query": {"data_state": "Unknown data state ID"}}
    )

    data_s = evaluate_from_dict(
        expression,
        query_args["start_time"],
        query_args["end_time"],
        data_state,
        query_args["bucket_width_value"],
        query_args["bucket_width_unit"],
        query_args["timezone"],
    )

    data_s = data_s.dropna().replace(np.nan, None)
    data_s.index = pd.Series(data_s.index).apply(lambda x: x.isoformat())

    return data_s.to_dict()
