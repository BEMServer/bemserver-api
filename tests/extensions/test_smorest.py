"""Test smorest extension"""


class TestSmorest:
    def test_get_token(self, app, users):
        user_1 = users["Active"]["user"]

        client = app.test_client()
        payload = {"email": user_1.email, "password": "@ctive"}
        resp = client.post("/auth/token", json=payload)
        assert resp.status_code == 201
        assert "token" in resp.json

        # Wrong password
        client = app.test_client()
        payload = {"email": user_1.email, "password": "dummy"}
        resp = client.post("/auth/token", json=payload)
        assert resp.status_code == 200

        # Wrong email
        client = app.test_client()
        payload = {"email": "dummy@dummy.com", "password": "dummy"}
        resp = client.post("/auth/token", json=payload)
        assert resp.status_code == 200
