"""Tasks by campaigns routes tests"""

from tests.common import AuthHeader

TASKS_URL = "/tasks/"


class TestTasks:
    def test_tasks_api(self, app, users, campaigns):
        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(TASKS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert isinstance(ret_val["tasks"], list)

    def test_tasks_as_user_api(self, app, users):
        user_creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(TASKS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert isinstance(ret_val["tasks"], list)

    def test_tasks_as_anonym_api(self, app):
        client = app.test_client()

        # GET list
        ret = client.get(TASKS_URL)
        assert ret.status_code == 401
