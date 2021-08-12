"""Campaign resources"""
from flask.views import MethodView
from flask_smorest import abort
import sqlalchemy as sqla

from bemserver_core.model import Campaign, UserByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import CampaignSchema, CampaignQueryArgsSchema


blp = Blueprint(
    'Campaign',
    __name__,
    url_prefix='/campaigns',
    description="Operations on campaigns"
)


@blp.route('/')
class CampaignViews(MethodView):

    @blp.login_required(role=["admin", "user"])
    @blp.etag
    @blp.arguments(CampaignQueryArgsSchema, location='query')
    @blp.response(200, CampaignSchema(many=True))
    def get(self, args):
        """List campaigns"""
        ret = db.session.query(Campaign).filter_by(**args)
        if blp.current_user() and not blp.current_user().is_admin:
            ret = ret.join(UserByCampaign).filter(
                UserByCampaign.user_id == blp.current_user().id
            )
        return ret

    @blp.login_required(role="admin")
    @blp.etag
    @blp.arguments(CampaignSchema)
    @blp.response(201, CampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new campaign"""
        item = Campaign.new(**new_item)
        db.session.commit()
        return item


@blp.route('/<int:item_id>')
class CampaignByIdViews(MethodView):

    @blp.login_required(role=["admin", "user"])
    @blp.etag
    @blp.response(200, CampaignSchema)
    def get(self, item_id):
        """Get campaign by ID"""
        item = db.session.get(Campaign, item_id)
        if item is None:
            abort(404)
        if blp.current_user() and not blp.current_user().is_admin:
            stmt = sqla.select(UserByCampaign).where(
                sqla.and_(
                    UserByCampaign.user_id == blp.current_user().id,
                    UserByCampaign.campaign_id == item_id
                )
            )
            if not db.session.execute(stmt).all():
                abort(403)
        return item

    @blp.login_required(role="admin")
    @blp.etag
    @blp.arguments(CampaignSchema)
    @blp.response(200, CampaignSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing campaign"""
        item = db.session.get(Campaign, item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, CampaignSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required(role="admin")
    @blp.etag
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a campaign"""
        item = db.session.get(Campaign, item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, CampaignSchema)
        db.session.delete(item)
        db.session.commit()
