"""TaskByCampaign resources"""

from flask.views import MethodView

from bemserver_core.scheduled_tasks import list_tasks

from bemserver_api import Blueprint

from .schemas import TasksSchema

blp = Blueprint(
    "Task",
    __name__,
    url_prefix="/tasks",
    description="Operations on tasks",
)


@blp.route("/")
class TaskViews(MethodView):
    @blp.login_required
    @blp.response(200, TasksSchema)
    def get(self):
        """List registered tasks"""
        return {"tasks": list_tasks()}
