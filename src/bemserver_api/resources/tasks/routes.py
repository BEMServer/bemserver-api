"""Tasks resources"""

from flask import current_app as current_flask_app

from flask_smorest import abort

from celery import current_app as current_celery_app

from bemserver_core.authorization import get_current_user
from bemserver_core.celery import BEMServerCoreAsyncTask

from bemserver_api import Blueprint

from .schemas import TaskRunSchema, TaskSchema

blp = Blueprint(
    "Task",
    __name__,
    url_prefix="/tasks",
    description="Operations on tasks",
)


@blp.route("/")
@blp.login_required
@blp.response(200, TaskSchema(many=True))
def get():
    """List registered tasks"""

    # Get schedules for each task
    bsc = current_flask_app.extensions["bemserver_core"]["app"]
    beat_schedule = bsc.config.get("CELERY_CONFIG", {}).get("beat_schedule", {})
    task_schedules = {}
    for name, value in beat_schedule.items():
        if (task := value.get("task")) and (schedule := value.get("schedule")):
            task_schedules.setdefault(task, {})[name] = schedule

    # Get tasks
    tasks = [
        {
            "name": name,
            "default_parameters": task.DEFAULT_PARAMETERS,
            "schedule": task_schedules.get(
                f"{name}{current_celery_app.SCHEDULED_TASKS_NAME_SUFFIX}", {}
            ),
        }
        for name, task in current_celery_app.tasks.items()
        if isinstance(task, BEMServerCoreAsyncTask)
    ]

    return tasks


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
            for name, task in current_celery_app.tasks.items()
            if isinstance(task, BEMServerCoreAsyncTask) and name == args["task_name"]
        )
    except StopIteration:
        abort(422, message="Unknown task")

    campaign_id = args["campaign_id"]
    start_dt = args["start_time"]
    end_dt = args["end_time"]
    task.delay(user.id, campaign_id, start_dt, end_dt, **args["parameters"])
