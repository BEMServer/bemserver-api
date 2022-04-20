"""TestPluginEnableCampaign resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_api import Blueprint
from bemserver_api.database import db

from ...model import TestPluginEnableCampaign
from .schemas import (
    TestPluginEnableCampaignSchema,
    TestPluginEnableCampaignQueryArgsSchema,
)


blp = Blueprint(
    "TestPluginEnableCampaign",
    __name__,
    url_prefix="/enable_campaigns",
)


@blp.route("/")
class TestPluginEnableCampaignViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TestPluginEnableCampaignQueryArgsSchema, location="query")
    @blp.response(200, TestPluginEnableCampaignSchema(many=True))
    def get(self, args):
        return TestPluginEnableCampaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TestPluginEnableCampaignSchema)
    @blp.response(201, TestPluginEnableCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        item = TestPluginEnableCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TestPluginEnableCampaignByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TestPluginEnableCampaignSchema)
    def get(self, item_id):
        item = TestPluginEnableCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TestPluginEnableCampaignSchema)
    @blp.response(200, TestPluginEnableCampaignSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        item = TestPluginEnableCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TestPluginEnableCampaignSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        item = TestPluginEnableCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TestPluginEnableCampaignSchema)
        item.delete()
        db.session.commit()
