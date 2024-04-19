"""Test authentication extension"""

import base64
import datetime as dt

import pytest

from joserfc import jwt
from joserfc.errors import ExpiredTokenError, MissingClaimError

from bemserver_core.authorization import get_current_user

from bemserver_api import Blueprint
from bemserver_api.extensions.authentication import auth


class TestAuthentication:
    def test_auth_encode_decode(self, app, users):
        user_1 = users["Active"]["user"]

        text = auth.encode(user_1)
        token = auth.decode(text)

        assert token.header == {"typ": "JWT", "alg": "HS256"}
        assert token.claims["email"] == "active@test.com"
        assert "exp" in token.claims
        auth.validate_token(token)

    def test_auth_decode_error(self, app):
        with pytest.raises(ValueError):
            auth.decode("dummy")

    def test_auth_validation_error(self, app):
        text = jwt.encode(auth.HEADER, {"email": "test@test.com", "exp": 0}, auth.key)
        token = auth.decode(text)
        with pytest.raises(ExpiredTokenError):
            auth.validate_token(token)

        text = jwt.encode(
            auth.HEADER, {"exp": dt.datetime.now(tz=dt.timezone.utc)}, auth.key
        )
        token = auth.decode(text)
        with pytest.raises(MissingClaimError):
            auth.validate_token(token)

    def test_auth_login_required_http_basic_auth(self, app, users):
        active_user_creds = users["Active"]["creds"]
        active_user_invalid_creds = base64.b64encode(
            f'{users["Active"]["user"].email}:bad_pwd'.encode()
        ).decode()
        inactive_user_creds = users["Inactive"]["creds"]
        api = app.extensions["flask-smorest"]["apis"][""]["ext_obj"]
        blp = Blueprint("AuthTest", __name__, url_prefix="/auth_test")

        @blp.route("/auth")
        @blp.login_required
        @blp.response(200)
        def auth_func():
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

        # Broken auth headers
        headers = {"Authorization": "Basic Dummy"}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204
        creds = base64.b64encode(b"Dummy").decode()
        headers = {"Authorization": "Basic " + creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Inactive user
        headers = {"Authorization": inactive_user_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 403
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Active user with invalid creds (bad password)
        headers = {"Authorization": active_user_invalid_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Active user
        headers = {"Authorization": active_user_creds}
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

    def test_auth_login_required_jwt(self, app, users):
        active_user_jwt = users["Active"]["jwt"]
        active_user_invalid_jwt = jwt.encode(
            auth.HEADER, {"email": "dummy@dummy.com"}, "Dummy"
        )
        inactive_user_jwt = users["Inactive"]["jwt"]
        api = app.extensions["flask-smorest"]["apis"][""]["ext_obj"]
        blp = Blueprint("AuthTest", __name__, url_prefix="/auth_test")

        @blp.route("/auth")
        @blp.login_required
        @blp.response(200)
        def auth_func():
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

        # Broken auth headers
        headers = {"Authorization": "Bearer Dummy"}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204
        creds = jwt.encode(auth.HEADER, {}, app.config["SECRET_KEY"])
        headers = {"Authorization": "Bearer " + creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Inactive user
        headers = {"Authorization": inactive_user_jwt}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 403
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Active user with invalid jwt (bad password)
        headers = {"Authorization": active_user_invalid_jwt}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Active user
        headers = {"Authorization": active_user_jwt}
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
