"""REST API extension"""
from copy import deepcopy
from functools import wraps
import http

import marshmallow as ma
import flask_smorest
from webargs.fields import DelimitedList
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.ext.marshmallow.common import resolve_schema_cls
import marshmallow_sqlalchemy as msa

from .ma_fields import Timezone
from .authentication import auth
from . import integrity_error


def resolver(schema):
    # This is the default name resolver from apispec
    schema_cls = resolve_schema_cls(schema)
    name = schema_cls.__name__
    if name.endswith("Schema"):
        name = name[:-6] or name
    # Except it appends ExcludeId to schemas where id is excluded.
    if isinstance(schema, ma.Schema) and "id" in schema.exclude:
        name = f"{name}ExcludeId"
    return name


class Api(flask_smorest.Api):
    """Api class"""

    def __init__(self, app=None, *, spec_kwargs=None):
        spec_kwargs = spec_kwargs or {}
        spec_kwargs["marshmallow_plugin"] = MarshmallowPlugin(
            schema_name_resolver=resolver
        )
        super().__init__(app=app, spec_kwargs=spec_kwargs)

    def init_app(self, app, *, spec_kwargs=None):
        super().init_app(app, spec_kwargs=spec_kwargs)
        self.register_field(Timezone, "string", "iana-tz")
        self.spec.components.security_scheme(
            "BasicAuthentication", {"type": "http", "scheme": "basic"}
        )


class Blueprint(flask_smorest.Blueprint):
    """Blueprint class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._prepare_doc_cbks.append(self._prepare_auth_doc)

    @staticmethod
    def login_required(func=None, **kwargs):
        def decorator(function):
            function = auth.login_required(**kwargs)(function)
            getattr(function, "_apidoc", {})["auth"] = True
            return function

        if func is None:
            return decorator
        return decorator(func)

    @staticmethod
    def _prepare_auth_doc(doc, doc_info, *, app, **kwargs):
        if doc_info.get("auth", False):
            doc.setdefault("responses", {})["401"] = http.HTTPStatus(401).name
            doc["security"] = [{"BasicAuthentication": []}]
        return doc

    @staticmethod
    def current_user():
        return auth.current_user()

    @staticmethod
    def catch_integrity_error(func=None):
        """Catch DB integrity errors"""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with integrity_error.catch_integrity_error():
                    return func(*args, **kwargs)

            # Store doc in wrapper function
            # The deepcopy avoids modifying the wrapped function doc
            wrapper._apidoc = deepcopy(getattr(wrapper, "_apidoc", {}))
            wrapper._apidoc.setdefault("response", {}).setdefault("responses", {})[
                409
            ] = http.HTTPStatus(409).name

            return wrapper

        if func is None:
            return decorator
        return decorator(func)


class Schema(ma.Schema):
    """Base Schema class to use in the API"""

    # Ensures the fields are ordered
    set_class = ma.orderedset.OrderedSet


class AutoSchema(msa.SQLAlchemyAutoSchema, Schema):
    """Auto Schema class used to load/dump SQLAlchemy objects

    The API assumes missing = None/null, so we treat missing fields as None
    unless they are read-only.
    """

    class Meta:
        include_fk = True

    @ma.post_load
    def set_missing_expected_values_to_none(self, data, **kwargs):
        loadable_fields = [k for k, v in self.fields.items() if not v.dump_only]
        for name in loadable_fields:
            data.setdefault(name, None)
        return data

    @ma.post_dump
    def remove_none_values(self, data, **kwargs):
        return {key: value for key, value in data.items() if value is not None}


class SQLCursorPage(flask_smorest.Page):
    """SQL cursor pager"""

    @property
    def item_count(self):
        return self.collection.count()


class SortField(DelimitedList):
    """Field used to specify sort order fields

    :param list fields: List of fields to sort upon, by order of priority (the
    first field is the first sort key). Each field is a field name, optionally
    prefixed with "+" or "-".
    """

    def __init__(self, fields, **kwargs):
        validator = ma.validate.OneOf(
            [v for f in fields for v in [f, f"+{f}", f"-{f}"]]
        )
        super().__init__(ma.fields.String(validate=validator), **kwargs)
