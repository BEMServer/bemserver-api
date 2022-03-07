"""Test authentication extension"""
from flask import jsonify

from bemserver_api import Blueprint

from bemserver_core.authorization import get_current_user


class TestAuthentication:
    def test_auth_login_required(self, app, users):

        active_user_creds = users["Active"]["creds"]
        active_user_invalid_creds = users["Active"]["invalid_creds"]
        inactive_user_creds = users["Inactive"]["creds"]
        api = app.extensions["flask-smorest"]["ext_obj"]
        blp = Blueprint("AuthTest", __name__, url_prefix="/auth_test")

        @blp.route("/auth")
        @blp.login_required
        @blp.response(200)
        def auth():
            return get_current_user().name

        @blp.route("/no_auth")
        @blp.response(204)
        def no_auth():
            return None

        api.register_blueprint(blp)
        client = app.test_client()

        # Anonymous user
        headers = {}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Inactive user
        headers = {"Authorization": "Basic " + inactive_user_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 403
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Active user with invalid creds (bad password)
        headers = {"Authorization": "Basic " + active_user_invalid_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Active user
        headers = {"Authorization": "Basic " + active_user_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 200
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Check OpenAPI spec
        spec = api.spec.to_dict()
        assert spec["components"]["securitySchemes"]["BasicAuthentication"] == {
            "type": "http",
            "scheme": "basic",
        }
        auth_spec = spec["paths"]["/auth_test/auth"]
        assert auth_spec["get"]["responses"]["401"] == {
            "$ref": "#/components/responses/UNAUTHORIZED"
        }
        assert auth_spec["get"]["security"] == [{"BasicAuthentication": []}]
        no_auth_spec = spec["paths"]["/auth_test/no_auth"]
        assert "401" not in no_auth_spec["get"]["responses"]
        assert "security" not in no_auth_spec["get"]

    def test_auth_current_user(self, app, users):

        active_user_creds = users["Active"]["creds"]
        api = app.extensions["flask-smorest"]["ext_obj"]

        blp = Blueprint("AuthTest", __name__, url_prefix="/auth_test")

        @blp.route("/user")
        @blp.login_required
        @blp.response(200)
        def user():
            return jsonify(blp.current_user().name)

        api.register_blueprint(blp)
        client = app.test_client()

        # Active user
        headers = {"Authorization": "Basic " + active_user_creds}
        resp = client.get("/auth_test/user", headers=headers)
        assert resp.json == "Active"
