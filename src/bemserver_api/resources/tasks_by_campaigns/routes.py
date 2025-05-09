"""TaskByCampaign resources"""

from flask.views import MethodView

from flask_smorest import abort

from bemserver_core.scheduled_tasks import TaskByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TaskByCampaignPutSchema,
    TaskByCampaignQueryArgsSchema,
    TaskByCampaignSchema,
)

blp = Blueprint(
    "TaskByCampaign",
    __name__,
    url_prefix="/tasks_by_campaigns",
    description="Operations on scheduled task x campaign associations",
)


@blp.route("/")
class TaskByCampaignViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TaskByCampaignQueryArgsSchema, location="query")
    @blp.response(200, TaskByCampaignSchema(many=True))
    def get(self, args):
        """List scheduled tasks x campaign associations"""
        return TaskByCampaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TaskByCampaignSchema)
    @blp.response(201, TaskByCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new tasks scheduled tasks x campaign association"""
        item = TaskByCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TaskByCampaignByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TaskByCampaignSchema)
    def get(self, item_id):
        """Get scheduled tasks x campaign association by ID"""
        item = TaskByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TaskByCampaignPutSchema)
    @blp.response(200, TaskByCampaignSchema)
    def put(self, item_data, item_id):
        """Update scheduled tasks x campaign association by ID"""
        item = TaskByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TaskByCampaignSchema)
        item.update(**item_data)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a scheduled tasks x campaign associations"""
        item = TaskByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TaskByCampaignSchema)
        item.delete()
        db.session.commit()
