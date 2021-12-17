"""Test integrity error"""
import sqlalchemy as sqla
import psycopg2.errors as ppe
import flask

import pytest

from bemserver_api import Api, Blueprint


uve = sqla.exc.IntegrityError(None, None, ppe.UniqueViolation())
fkve = sqla.exc.IntegrityError(None, None, ppe.ForeignKeyViolation())
uve = sqla.exc.IntegrityError(None, None, None)


class TestIntegrityError:
    @pytest.mark.parametrize("error", (uve, fkve, uve))
    def test_blp_integrity_error(self, error):

        app = flask.Flask("Test")
        api = Api(
            app, spec_kwargs={"title": "Test", "version": "1", "openapi_version": "3"}
        )

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

        resp = client.get("/test/decorator")
        assert resp.status_code == 409
        resp = client.get("/test/decorator_factory")
        assert resp.status_code == 409
