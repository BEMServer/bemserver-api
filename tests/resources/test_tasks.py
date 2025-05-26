"""Tasks by campaigns routes tests"""

import datetime as dt
from unittest import mock

import pytest

from celery import current_app as current_celery_app
from tests.common import AuthHeader

from bemserver_core.celery import (
    BEMServerCoreAsyncTask,
    BEMServerCoreScheduledTask,
)

TASKS_URL = "/tasks/"


def dummy_function():
    """Dummy fonction"""


@pytest.fixture
def celery_tasks():
    @current_celery_app.register_task
    class Dummy(BEMServerCoreAsyncTask):
        TASK_FUNCTION = dummy_function
        DEFAULT_PARAMETERS = {"a_1": "1", "a_2": 2}


CELERY_CONFIG = {
    "beat_schedule": {
        "dummy_task": {
            "task": "DummyScheduled",
            "schedule": 42,
        },
    },
}


class TestTasks:
    @pytest.mark.usefixtures("celery_tasks")
    @pytest.mark.parametrize(
        "bsc_config", ({"CELERY_CONFIG": CELERY_CONFIG},), indirect=True
    )
    def test_tasks_api(self, app, users, campaigns):
        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(TASKS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            for task in ret_val:
                assert isinstance(task["name"], str)
                assert isinstance(task["default_parameters"], dict)
            assert {
                "name": "Dummy",
                "default_parameters": {"a_1": "1", "a_2": 2},
                "schedule": {"dummy_task": "42"},
            } in ret_val

    def test_tasks_as_user_api(self, app, users):
        user_creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(TASKS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            for task in ret_val:
                assert isinstance(task["name"], str)
                assert isinstance(task["default_parameters"], dict)

    def test_tasks_as_anonym_api(self, app):
        client = app.test_client()

        # GET list
        ret = client.get(TASKS_URL)
        assert ret.status_code == 401

    def test_task_run_api(self, app, users, campaigns):
        user_1 = users["Active"]
        creds = user_1["creds"]

        campaign_1_id = campaigns[0]
        start_dt = dt.datetime(2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
        end_dt = dt.datetime(2020, 1, 2, 0, 0, tzinfo=dt.timezone.utc)

        client = app.test_client()

        task_mock = mock.MagicMock(spec=BEMServerCoreAsyncTask)

        with mock.patch(
            "bemserver_core.celery.BEMServerCoreCelery.tasks",
            new_callable=mock.PropertyMock,
            return_value={"Task": task_mock},
        ):
            with AuthHeader(creds):
                ret = client.post(
                    f"{TASKS_URL}run",
                    json={
                        "task_name": "Task",
                        "campaign_id": campaign_1_id,
                        "start_time": start_dt.isoformat(),
                        "end_time": end_dt.isoformat(),
                        "parameters": {"param_1": "value_1", "param_2": "value_2"},
                    },
                )
                assert ret.status_code == 204
                task_mock.delay.assert_called_with(
                    user_1["id"],
                    campaign_1_id,
                    start_dt,
                    end_dt,
                    **{"param_1": "value_1", "param_2": "value_2"},
                )

        task_mock = mock.MagicMock(spec=BEMServerCoreScheduledTask)

        with mock.patch(
            "bemserver_core.celery.BEMServerCoreCelery.tasks",
            new_callable=mock.PropertyMock,
            return_value={"Task": task_mock},
        ):
            with AuthHeader(creds):
                # Task not BEMServerCoreAsyncTask
                ret = client.post(
                    f"{TASKS_URL}run",
                    json={
                        "task_name": "Task",
                        "campaign_id": campaign_1_id,
                        "start_time": start_dt.isoformat(),
                        "end_time": end_dt.isoformat(),
                        "parameters": {"param_1": "value_1", "param_2": "value_2"},
                    },
                )
                assert ret.status_code == 422
                # Unknown task
                ret = client.post(
                    f"{TASKS_URL}run",
                    json={
                        "task_name": "Dummy",
                        "campaign_id": campaign_1_id,
                        "start_time": start_dt.isoformat(),
                        "end_time": end_dt.isoformat(),
                    },
                )
                assert ret.status_code == 422
