"""REST API extension"""
import http

import marshmallow as ma
import flask_smorest
import marshmallow_sqlalchemy as msa

from .ma_fields import Timezone
from .authentication import auth


class Api(flask_smorest.Api):
    """Api class"""
    def init_app(self, app, *, spec_kwargs=None):
        super().init_app(app, spec_kwargs=spec_kwargs)
        self.register_field(Timezone, 'string', 'IANA timezone')
        if app.config.get("AUTH_ENABLED", False):
            self.spec.components.security_scheme(
                "BasicAuthentication", {"type": "http", "scheme": "basic"}
            )


class Blueprint(flask_smorest.Blueprint):
    """Blueprint class"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._prepare_doc_cbks.append(self._prepare_auth_doc)

    @staticmethod
    def login_required(func):
        # Note: we don't use "role" and "optional" parameters in the app,
        # we always call login_required with no parameter
        func = auth.login_required(func)
        getattr(func, "_apidoc", {})["auth"] = True
        return func

    @staticmethod
    def _prepare_auth_doc(doc, doc_info, **kwargs):
        if doc_info.get("auth", False):
            doc.setdefault("responses", {})["401"] = http.HTTPStatus(401).name
            doc["security"] = [{"BasicAuthentication": []}]
        return doc

    @staticmethod
    def current_user():
        return auth.current_user()


class Schema(ma.Schema):
    """Schema class"""

    # Ensures the fields are ordered
    set_class = ma.orderedset.OrderedSet

    def update(self, obj, data):
        """Update object nullifying missing data"""
        loadable_fields = [
            k for k, v in self.fields.items() if not v.dump_only
        ]
        for name in loadable_fields:
            setattr(obj, name, data.get(name))

    # The API assumes missing = None/null
    @ma.post_dump
    def remove_none_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value is not None
        }


class AutoSchema(msa.SQLAlchemyAutoSchema, Schema):
    """Auto-schema class"""


class SQLCursorPage(flask_smorest.Page):
    """SQL cursor pager"""

    @property
    def item_count(self):
        return self.collection.count()
