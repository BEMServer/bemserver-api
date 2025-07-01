"""Tasks resources"""

from flask import current_app as current_flask_app

from flask_smorest import abort

from celery import current_app as current_celery_app
from celery.result import AsyncResult

from bemserver_core.authorization import get_current_user
from bemserver_core.celery import BEMServerCoreAsyncTask, BEMServerCoreScheduledTask

from bemserver_api import Blueprint

from .schemas import (
    TaskListSchema,
    TaskRunArgsSchema,
    TaskRunResponseSchema,
    TaskStatusSchema,
)

blp = Blueprint(
    "Task",
    __name__,
    url_prefix="/tasks",
    description="Operations on tasks",
)


@blp.route("/")
@blp.login_required
@blp.response(200, TaskListSchema)
def get_tasks():
    """List registered tasks"""

    # Get schedules for each task
    bsc = current_flask_app.extensions["bemserver_core"]["app"]
    beat_schedule = bsc.config.get("CELERY_CONFIG", {}).get("beat_schedule", {})
    task_schedules = {}
    for name, value in beat_schedule.items():
        if (task := value.get("task")) and (schedule := value.get("schedule")):
            task_schedules.setdefault(task, {})[name] = schedule

    # Get async tasks
    async_tasks = [
        {
            "name": name,
            "default_parameters": task.DEFAULT_PARAMETERS,
        }
        for name, task in current_celery_app.tasks.items()
        if isinstance(task, BEMServerCoreAsyncTask)
    ]

    # Get scheduled tasks
    scheduled_tasks = [
        {
            "name": name,
            "default_parameters": task.DEFAULT_PARAMETERS,
            "schedule": task_schedules.get(name),
            "async_task": task.ASYNC_TASK.name if task.ASYNC_TASK is not None else None,
        }
        for name, task in current_celery_app.tasks.items()
        if isinstance(task, BEMServerCoreScheduledTask)
    ]

    return {
        "async_tasks": async_tasks,
        "scheduled_tasks": scheduled_tasks,
    }


@blp.route("/run", methods=["POST"])
@blp.login_required
@blp.arguments(TaskRunArgsSchema)
@blp.response(200, TaskRunResponseSchema)
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
    task = task.delay(user.id, campaign_id, start_dt, end_dt, **args["parameters"])
    return {"task_id": task.id}


@blp.route("/<task_id>")
@blp.login_required
@blp.response(200, TaskStatusSchema)
def get_task_status(task_id):
    """Get task status"""
    task = AsyncResult(task_id)
    if task.state == "PENDING":
        abort(
            404,
            message=(
                f"Unknown task ID: {task_id}. "
                "Either the task ID is wrong or the task was deleted."
            ),
        )
    ret = {"task_id": task_id, "status": task.state}
    if task.state in ("PROGRESS", "SUCCESS") and task.info is not None:
        ret["info"] = task.info
    return ret
