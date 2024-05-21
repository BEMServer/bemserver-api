"""REST API extension"""

import http
from copy import deepcopy
from functools import wraps

import flask

import flask_smorest
import marshmallow as ma
import marshmallow_sqlalchemy as msa
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.ext.marshmallow.common import resolve_schema_cls

from . import integrity_error
from .authentication import auth
from .ma_fields import Timezone


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


SECURITY_SCHEMES = {
    "Bearer": (
        "BearerAuthentication",
        {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
    ),
    "Basic": (
        "BasicAuthentication",
        {"type": "http", "scheme": "basic"},
    ),
}


class Api(flask_smorest.Api):
    """Api class"""

    def __init__(self, app=None, *, spec_kwargs=None):
        spec_kwargs = spec_kwargs or {}
        spec_kwargs["marshmallow_plugin"] = MarshmallowPlugin(
            schema_name_resolver=resolver
        )
        super().__init__(app=app, spec_kwargs=spec_kwargs)

    def init_app(self, app, *, spec_kwargs=None):
        spec_kwargs = spec_kwargs or {}
        spec_kwargs["security"] = [
            {SECURITY_SCHEMES[scheme][0]: []} for scheme in app.config["AUTH_METHODS"]
        ]
        super().init_app(app, spec_kwargs=spec_kwargs)
        self.register_field(Timezone, "string", "iana-tz")
        self.register_blueprint(auth_blp)
        for scheme in app.config["AUTH_METHODS"]:
            self.spec.components.security_scheme(*SECURITY_SCHEMES[scheme])


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
        else:
            doc["security"] = []
        return doc

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
            (
                wrapper._apidoc.setdefault("response", {})
                .setdefault("responses", {})
                .setdefault(409, [])
                .append(http.HTTPStatus(409).name)
            )

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


auth_blp = Blueprint(
    "Authentication",
    __name__,
    url_prefix="/auth",
    description="Authentication operations",
)


class GetJWTArgsSchema(Schema):
    email = ma.fields.Email(required=True)
    password = ma.fields.String(validate=ma.validate.Length(1, 80), required=True)


class GetJWTRespSchema(Schema):
    status = ma.fields.String(validate=ma.validate.OneOf(("success", "failure")))
    token = ma.fields.String()


@auth_blp.route("/token", methods=["POST"])
@auth_blp.arguments(GetJWTArgsSchema)
@auth_blp.response(
    200,
    GetJWTRespSchema,
    examples={
        "success": {
            "value": {
                "status": "success",
                "token": (
                    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.u"
                    "JKHM4XyWv1bC_-rpkjK19GUy0Fgrkm_pGHi8XghjWM"
                ),
            },
        },
        "failure": {
            "value": {
                "status": "failure",
            },
        },
    },
)
def get_token(creds):
    """Get an authentication token"""
    user = auth.get_user_by_email(creds["email"])
    if user is None or not user.check_password(creds["password"]) or not user.is_active:
        return flask.jsonify({"status": "failure"})
    return {"status": "success", "token": auth.encode(user).decode("utf-8")}
