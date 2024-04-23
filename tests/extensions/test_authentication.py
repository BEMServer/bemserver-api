"""Test authentication extension"""

import base64
import datetime as dt

import pytest

from joserfc import jwt
from joserfc.errors import ExpiredTokenError, MissingClaimError
from tests.common import TestConfig

from bemserver_core.authorization import get_current_user

from bemserver_api import Blueprint
from bemserver_api.extensions.authentication import auth


class HBATestConfig(TestConfig):
    AUTH_METHODS = [
        "Basic",
    ]


class JWTTestConfig(TestConfig):
    AUTH_METHODS = [
        "Bearer",
    ]


class TestAuthentication:
    def test_auth_encode_decode(self, app, users):
        user_1 = users["Active"]["user"]

        text = auth.encode(user_1)
        token = auth.decode(text)

        assert token.header == {"typ": "JWT", "alg": "HS256"}
        assert token.claims["email"] == user_1.email
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

    @pytest.mark.parametrize("app", (HBATestConfig,), indirect=True)
    def test_auth_login_required_http_basic_auth(self, app, users):
        active_user_hba_creds = users["Active"]["hba_creds"]
        active_user_invalid_hba_creds = base64.b64encode(
            f'{users["Active"]["user"].email}:bad_pwd'.encode()
        ).decode()
        inactive_user_hba_creds = users["Inactive"]["hba_creds"]
        active_user_jwt = users["Active"]["creds"]
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
        assert resp.headers["WWW-Authenticate"] == "Basic"
        assert resp.json["errors"]["authentication"] == "missing_authentication"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Broken auth headers
        headers = {"Authorization": "Basic Dummy"}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        assert resp.headers["WWW-Authenticate"] == "Basic"
        assert resp.json["errors"]["authentication"] == "malformed_credentials"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204
        hba_creds = base64.b64encode(b"Dummy").decode()
        headers = {"Authorization": "Basic " + hba_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        assert resp.headers["WWW-Authenticate"] == "Basic"
        assert resp.json["errors"]["authentication"] == "malformed_credentials"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Wrong scheme
        headers = {"Authorization": active_user_jwt}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        assert resp.headers["WWW-Authenticate"] == "Basic"
        assert resp.json["errors"]["authentication"] == "invalid_scheme"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Inactive user
        headers = {"Authorization": inactive_user_hba_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 403
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Active user with invalid creds (wrong password)
        headers = {"Authorization": "Basic " + active_user_invalid_hba_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        assert resp.headers["WWW-Authenticate"] == "Basic"
        assert resp.json["errors"]["authentication"] == "invalid_credentials"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Active user
        headers = {"Authorization": active_user_hba_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 200
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Check OpenAPI spec
        spec = api.spec.to_dict()
        assert spec["security"] == [{"BasicAuthentication": []}]
        assert spec["components"]["securitySchemes"] == {
            "BasicAuthentication": {
                "type": "http",
                "scheme": "basic",
            }
        }
        auth_spec = spec["paths"]["/auth_test/auth"]
        assert auth_spec["get"]["responses"]["401"] == {
            "$ref": "#/components/responses/UNAUTHORIZED"
        }
        assert "security" not in auth_spec["get"]
        no_auth_spec = spec["paths"]["/auth_test/no_auth"]
        assert "401" not in no_auth_spec["get"]["responses"]
        assert no_auth_spec["get"]["security"] == []

    @pytest.mark.parametrize("app", (JWTTestConfig,), indirect=True)
    def test_auth_login_required_jwt(self, app, users):
        user_1 = users["Active"]["user"]
        active_user_jwt_creds = users["Active"]["creds"]
        active_user_invalid_jwt_creds = jwt.encode(
            auth.HEADER, {"email": "dummy@dummy.com"}, "Dummy"
        )
        inactive_user_jwt_creds = users["Inactive"]["creds"]
        active_user_hba_creds = users["Active"]["hba_creds"]
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
        assert resp.headers["WWW-Authenticate"] == "Bearer"
        assert resp.json["errors"]["authentication"] == "missing_authentication"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Malformed token
        headers = {"Authorization": "Bearer Dummy"}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        assert resp.headers["WWW-Authenticate"] == "Bearer"
        assert resp.json["errors"]["authentication"] == "malformed_token"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Missing claims
        creds = jwt.encode(auth.HEADER, {}, app.config["SECRET_KEY"])
        headers = {"Authorization": "Bearer " + creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        assert resp.headers["WWW-Authenticate"] == "Bearer"
        assert resp.json["errors"]["authentication"] == "invalid_token"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Wrong scheme
        headers = {"Authorization": active_user_hba_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        assert resp.headers["WWW-Authenticate"] == "Bearer"
        assert resp.json["errors"]["authentication"] == "invalid_scheme"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Bad signature
        headers = {"Authorization": "Bearer " + active_user_invalid_jwt_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        assert resp.headers["WWW-Authenticate"] == "Bearer"
        assert resp.json["errors"]["authentication"] == "malformed_token"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Expired token
        headers = {
            "Authorization": "Bearer "
            + jwt.encode(
                auth.HEADER, {"email": user_1.email, "exp": 0}, app.config["SECRET_KEY"]
            )
        }
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 401
        assert resp.headers["WWW-Authenticate"] == "Bearer"
        assert resp.json["errors"]["authentication"] == "expired_token"
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Inactive user
        headers = {"Authorization": inactive_user_jwt_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 403
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Active user
        headers = {"Authorization": active_user_jwt_creds}
        resp = client.get("/auth_test/auth", headers=headers)
        assert resp.status_code == 200
        resp = client.get("/auth_test/no_auth", headers=headers)
        assert resp.status_code == 204

        # Check OpenAPI spec
        spec = api.spec.to_dict()
        assert spec["security"] == [{"BearerAuthentication": []}]
        assert spec["components"]["securitySchemes"] == {
            "BearerAuthentication": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
        auth_spec = spec["paths"]["/auth_test/auth"]
        assert auth_spec["get"]["responses"]["401"] == {
            "$ref": "#/components/responses/UNAUTHORIZED"
        }
        assert "security" not in auth_spec["get"]
        no_auth_spec = spec["paths"]["/auth_test/no_auth"]
        assert "401" not in no_auth_spec["get"]["responses"]
        assert no_auth_spec["get"]["security"] == []
