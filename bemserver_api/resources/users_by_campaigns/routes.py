"""Users by campaigns resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import UserByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import UserByCampaignSchema, UserByCampaignQueryArgsSchema


blp = Blueprint(
    'UserByCampaign',
    __name__,
    url_prefix='/usersbycampaigns',
    description="Operations on users x campaigns associations"
)


@blp.route('/')
class UserByCampaignViews(MethodView):

    @blp.login_required(role=["admin", "user"])
    @blp.etag
    @blp.arguments(UserByCampaignQueryArgsSchema, location='query')
    @blp.response(200, UserByCampaignSchema(many=True))
    def get(self, args):
        """List campaign x user associations"""
        return UserByCampaign.get(**args)

    @blp.login_required(role="admin")
    @blp.etag
    @blp.arguments(UserByCampaignSchema)
    @blp.response(201, UserByCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new campaign x user association"""
        item = UserByCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route('/<int:item_id>')
class UserByCampaignByIdViews(MethodView):

    @blp.login_required(role=["admin", "user"])
    @blp.etag
    @blp.response(200, UserByCampaignSchema)
    def get(self, item_id):
        """Get campaign x user association by ID"""
        item = UserByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required(role="admin")
    @blp.response(204)
    def delete(self, item_id):
        """Delete a campaign x user association"""
        item = UserByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
