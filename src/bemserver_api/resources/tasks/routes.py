"""Tasks resources"""

from flask_smorest import abort

from celery import current_app

from bemserver_core.authorization import get_current_user
from bemserver_core.tasks import (
    BEMServerCoreAsyncTask,
    BEMServerCoreScheduledTask,
)

from bemserver_api import Blueprint

from .schemas import TaskRunSchema, TasksSchema

blp = Blueprint(
    "Task",
    __name__,
    url_prefix="/tasks",
    description="Operations on tasks",
)


@blp.route("/")
@blp.login_required
@blp.response(200, TasksSchema)
def get():
    """List registered tasks"""
    async_tasks = [
        {
            "name": name,
            "default_parameters": task.DEFAULT_PARAMETERS,
        }
        for name, task in current_app.tasks.items()
        if isinstance(task, BEMServerCoreAsyncTask)
    ]
    scheduled_tasks = [
        {
            "name": name,
            "default_parameters": task.DEFAULT_PARAMETERS,
        }
        for name, task in current_app.tasks.items()
        if isinstance(task, BEMServerCoreScheduledTask)
    ]

    return {"async_tasks": async_tasks, "scheduled_tasks": scheduled_tasks}


@blp.route("/run", methods=["POST"])
@blp.login_required
@blp.arguments(TaskRunSchema)
@blp.response(204)
def run(args):
    """Run async task"""
    user = get_current_user()

    try:
        task = next(
            task
            for name, task in current_app.tasks.items()
            if isinstance(task, BEMServerCoreAsyncTask) and name == args["task_name"]
        )
    except StopIteration:
        abort(422, message="Unknown task")

    campaign_id = args["campaign_id"]
    start_dt = args["start_time"]
    end_dt = args["end_time"]
    task.delay(user.id, campaign_id, start_dt, end_dt, **args["parameters"])
