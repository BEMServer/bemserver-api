"""Tasks by campaigns routes tests"""

from copy import deepcopy

import pytest

from tests.common import AuthHeader

DUMMY_ID = "69"

TASKS_BY_CAMPAIGNS_URL = "/tasks_by_campaigns/"


class TestTaskByCampaignApi:
    def test_tasks_by_campaigns_api(self, app, users, campaigns):
        creds = users["Chuck"]["creds"]
        campaign_1_id = campaigns[0]
        campaign_2_id = campaigns[1]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(TASKS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            task_1 = {"task_name": "Task 1", "campaign_id": campaign_1_id}
            ret = client.post(TASKS_BY_CAMPAIGNS_URL, json=task_1)
            assert ret.status_code == 201
            ret_val = ret.json
            task_1_id = ret_val.pop("id")
            task_1_etag = ret.headers["ETag"]
            task_1_expected = deepcopy(task_1)
            task_1_expected["is_enabled"] = True
            assert ret_val == task_1_expected

            # POST violating unique constraint
            ret = client.post(TASKS_BY_CAMPAIGNS_URL, json=task_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TASKS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == task_1_id

            # GET by id
            ret = client.get(f"{TASKS_BY_CAMPAIGNS_URL}{task_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == task_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == task_1_expected

            # PUT
            task_1_expected["is_enabled"] = False
            task_1_expected["parameters"] = {"dummy": 42}
            ret = client.put(
                f"{TASKS_BY_CAMPAIGNS_URL}{task_1_id}",
                json={"is_enabled": False, "parameters": {"dummy": 42}},
                headers={"If-Match": task_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            task_1_etag = ret.headers["ETag"]
            assert ret_val == task_1_expected

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TASKS_BY_CAMPAIGNS_URL}{DUMMY_ID}",
                json={"is_enabled": False},
                headers={"If-Match": task_1_etag},
            )
            assert ret.status_code == 404

            # POST campaign 2
            task_2 = {"task_name": "Task 2", "campaign_id": campaign_2_id}
            ret = client.post(TASKS_BY_CAMPAIGNS_URL, json=task_2)
            ret_val = ret.json
            task_2_id = ret_val.pop("id")
            task_2_etag = ret.headers["ETag"]

            # GET list
            ret = client.get(TASKS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                TASKS_BY_CAMPAIGNS_URL,
                query_string={"campaign_id": campaign_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == task_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{TASKS_BY_CAMPAIGNS_URL}{DUMMY_ID}",
                headers={"If-Match": task_1_etag},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{TASKS_BY_CAMPAIGNS_URL}{task_1_id}",
                headers={"If-Match": task_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{TASKS_BY_CAMPAIGNS_URL}{task_2_id}",
                headers={"If-Match": task_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(TASKS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{TASKS_BY_CAMPAIGNS_URL}{task_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_tasks_by_campaigns_as_user_api(
        self, app, users, campaigns, tasks_by_campaigns
    ):
        user_creds = users["Active"]["creds"]
        campaign_1_id = campaigns[0]
        task_1_id = tasks_by_campaigns[0]
        task_2_id = tasks_by_campaigns[1]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(TASKS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            task_1 = ret_val[0]
            assert task_1["id"] == task_1_id

            # POST
            task_3 = {"task_name": "Task 3", "campaign_id": campaign_1_id}
            ret = client.post(TASKS_BY_CAMPAIGNS_URL, json=task_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TASKS_BY_CAMPAIGNS_URL}{task_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert ret_val["id"] == task_1_id
            task_1_etag = ret.headers["ETag"]
            ret = client.get(f"{TASKS_BY_CAMPAIGNS_URL}{task_2_id}")
            assert ret.status_code == 403

            # PUT
            ret = client.put(
                f"{TASKS_BY_CAMPAIGNS_URL}{task_1_id}",
                json={"is_enabled": False},
                headers={"If-Match": task_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TASKS_BY_CAMPAIGNS_URL}{task_1_id}",
                headers={"If-Match": task_1_etag},
            )
            assert ret.status_code == 403

    def test_tasks_by_campaigns_as_anonym_api(self, app, campaigns, tasks_by_campaigns):
        campaign_1_id = campaigns[0]
        task_1_id = tasks_by_campaigns[0]

        client = app.test_client()

        # GET list
        ret = client.get(TASKS_BY_CAMPAIGNS_URL)
        assert ret.status_code == 401

        # POST
        task_3 = {"task_name": "Task 3", "campaign_id": campaign_1_id}
        ret = client.post(TASKS_BY_CAMPAIGNS_URL, json=task_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TASKS_BY_CAMPAIGNS_URL}{task_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(
            f"{TASKS_BY_CAMPAIGNS_URL}{task_1_id}",
            json={"is_enabled": False},
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TASKS_BY_CAMPAIGNS_URL}{task_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
