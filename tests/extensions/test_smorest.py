"""Test smorest extension"""

import pytest

from tests.common import AuthHeader, TestConfig, make_token

from bemserver_api.extensions.authentication import auth


class HBATestConfig(TestConfig):
    AUTH_METHODS = [
        "Basic",
    ]


class TestSmorest:
    def test_get_token(self, app, users):
        user_1 = users["Active"]["user"]
        user_2 = users["Inactive"]["user"]

        client = app.test_client()
        payload = {"email": user_1.email, "password": "@ctive"}
        resp = client.post("/auth/token", json=payload)
        assert resp.status_code == 200
        assert resp.json["status"] == "success"
        claims = auth.decode(resp.json["access_token"])
        assert claims["email"] == user_1.email
        assert "exp" in claims
        assert claims["type"] == "access"
        claims.validate()
        claims = auth.decode(resp.json["refresh_token"])
        assert claims["email"] == user_1.email
        assert "exp" in claims
        assert claims["type"] == "refresh"
        claims.validate()

        # Inactive user
        client = app.test_client()
        payload = {"email": user_2.email, "password": "in@ctive"}
        resp = client.post("/auth/token", json=payload)
        assert resp.status_code == 200
        assert resp.json == {"status": "failure"}

        # Inactive user
        client = app.test_client()
        payload = {"email": user_2.email, "password": "in@ctive"}
        resp = client.post("/auth/token", json=payload)
        assert resp.status_code == 200
        assert resp.json == {"status": "failure"}

        # Wrong password
        client = app.test_client()
        payload = {"email": user_1.email, "password": "dummy"}
        resp = client.post("/auth/token", json=payload)
        assert resp.status_code == 200
        assert resp.json == {"status": "failure"}

        # Wrong email
        client = app.test_client()
        payload = {"email": "dummy@dummy.com", "password": "dummy"}
        resp = client.post("/auth/token", json=payload)
        assert resp.status_code == 200
        assert resp.json == {"status": "failure"}

    def test_refresh_token(self, app, users):
        user_1 = users["Active"]["user"]

        access_token = "Bearer " + make_token(user_1.email, "access")
        refresh_token = "Bearer " + make_token(user_1.email, "refresh")

        client = app.test_client()

        # No token
        resp = client.post("/auth/token/refresh")
        assert resp.status_code == 401

        # Acccess token
        with AuthHeader(access_token):
            resp = client.post("/auth/token/refresh")
        assert resp.status_code == 401

        # Refresh token
        with AuthHeader(refresh_token):
            resp = client.post("/auth/token/refresh")
        assert resp.status_code == 200
        assert resp.json["status"] == "success"
        claims = auth.decode(resp.json["access_token"])
        assert claims["email"] == user_1.email
        assert "exp" in claims
        assert claims["type"] == "access"
        claims.validate()
        claims = auth.decode(resp.json["refresh_token"])
        assert claims["email"] == user_1.email
        assert "exp" in claims
        assert claims["type"] == "refresh"
        claims.validate()

    @pytest.mark.parametrize("app", (HBATestConfig,), indirect=True)
    def test_token_routes_jwt_disabled(self, app, users):
        user_1 = users["Active"]["user"]

        client = app.test_client()
        payload = {"email": user_1.email, "password": "@ctive"}
        resp = client.post("/auth/token", json=payload)
        assert resp.status_code == 404

        access_token = "Bearer " + make_token(user_1.email, "access")
        with AuthHeader(access_token):
            resp = client.post("/auth/token/refresh")
        assert resp.status_code == 404
