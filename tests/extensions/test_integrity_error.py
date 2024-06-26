"""Test integrity error"""

import pytest

import psycopg.errors as ppe
import sqlalchemy as sqla

from bemserver_api import Blueprint


class TestIntegrityError:
    @pytest.mark.parametrize(
        ("error", "message"),
        (
            (
                sqla.exc.IntegrityError(None, None, ppe.UniqueViolation()),
                "Unique constraint violation",
            ),
            (
                sqla.exc.IntegrityError(None, None, ppe.ForeignKeyViolation()),
                "Foreign key constraint violation",
            ),
            (
                sqla.exc.IntegrityError(None, None, None),
                None,
            ),
        ),
    )
    def test_blp_integrity_error(self, app, error, message):
        api = app.extensions["flask-smorest"]["apis"][""]["ext_obj"]

        blp = Blueprint("Test", __name__, url_prefix="/test")

        @blp.route("/decorator")
        @blp.response(200)
        @blp.catch_integrity_error()
        def decorator():
            raise error

        @blp.route("/decorator_factory")
        @blp.response(200)
        @blp.catch_integrity_error
        def decorator_factory():
            raise error

        api.register_blueprint(blp)
        client = app.test_client()

        for url in ("/test/decorator", "/test/decorator_factory"):
            resp = client.get(url)
            assert resp.status_code == 409
            assert resp.json.get("message") == message
