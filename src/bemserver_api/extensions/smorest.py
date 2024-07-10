"""REST API extension"""

import http
from copy import deepcopy
from functools import wraps
from textwrap import dedent

import flask

import flask_smorest
import marshmallow as ma
import marshmallow_sqlalchemy as msa
from apispec.ext.marshmallow import MarshmallowPlugin as MarshmallowPluginOrig
from apispec.ext.marshmallow import OpenAPIConverter as OrigOpenAPIConverter
from apispec.ext.marshmallow.common import resolve_schema_cls

from bemserver_core.authorization import get_current_user

from . import integrity_error
from .authentication import auth
from .ma_fields import DictStr, Timezone


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


class OpenAPIConverter(OrigOpenAPIConverter):
    def _field2parameter(self, field, *, name, location):
        ret: dict = {"in": location, "name": name}

        prop = self.field2property(field)
        if self.openapi_version.major < 3:
            ret.update(prop)
        else:
            if "description" in prop:
                ret["description"] = prop.pop("description")
            if "deprecated" in prop:
                ret["deprecated"] = prop.pop("deprecated")
            ret["schema"] = prop

        # Document DictStr as "content" parameter
        # https://github.com/marshmallow-code/apispec/issues/922
        if isinstance(field, DictStr):
            ret["content"] = {"application/json": {"schema": ret.pop("schema")}}

        for param_attr_func in self.parameter_attribute_functions:
            ret.update(param_attr_func(field, ret=ret))

        return ret


class MarshmallowPlugin(MarshmallowPluginOrig):
    Converter = OpenAPIConverter


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
        if "Bearer" in app.config["AUTH_METHODS"]:
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


AUTH_BLP_DESC = dedent("""Authentication operations

The following resources are used to get and refresh tokens. When authenticating, first
get a couple of access (short-lived) and refresh (long-lived) tokens using login and
password. When or before access token expires, refresh tokens to get a new pair of
tokens with new expiration dates. If refresh token is expired, get a new pair of tokens
using login and password again.
""")


auth_blp = Blueprint(
    "Authentication",
    __name__,
    url_prefix="/auth",
    description=AUTH_BLP_DESC,
)


class GetJWTArgsSchema(Schema):
    email = ma.fields.Email(required=True)
    password = ma.fields.String(validate=ma.validate.Length(1, 80), required=True)


class GetJWTRespSchema(Schema):
    status = ma.fields.String(validate=ma.validate.OneOf(("success", "failure")))
    access_token = ma.fields.String()
    refresh_token = ma.fields.String()


@auth_blp.route("/token", methods=["POST"])
@auth_blp.arguments(GetJWTArgsSchema)
@auth_blp.response(
    200,
    GetJWTRespSchema,
    examples={
        "success": {
            "value": {
                "status": "success",
                "access_token": (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl"
                    "bWFpbCI6ImFjdGl2ZUB0ZXN0LmNvbSIsImV4cCI6M"
                    "TcxNjM2OTg4OCwidHlwZSI6ImFjY2VzcyJ9.YT-50"
                    "7Qo9oncWKKRJhRXBbpLrOCYoJOMxbk1IaAQef4"
                ),
                "refresh_token": (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl"
                    "bWFpbCI6ImFjdGl2ZUB0ZXN0LmNvbSIsImV4cCI6M"
                    "TcyMTU1MzEzNSwidHlwZSI6InJlZnJlc2gifQ._kc"
                    "SHTzcngWIt-LRX6yBx8ftpekT_Dqo8qbPyfgFjSQ"
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
    """Get access and refresh tokens

    Use login and password to get a pair of access and refresh tokens.

    No authentication header needed. Credentials must be passed in request payload.
    """
    user = auth.get_user_by_email(creds["email"])
    if user is None or not user.check_password(creds["password"]) or not user.is_active:
        return flask.jsonify({"status": "failure"})
    return {
        "status": "success",
        "access_token": auth.encode(user).decode("utf-8"),
        "refresh_token": auth.encode(user, token_type="refresh").decode("utf-8"),
    }


@auth_blp.route("/token/refresh", methods=["POST"])
@auth_blp.login_required(refresh=True)
@auth_blp.response(
    200,
    GetJWTRespSchema,
    examples={
        "success": {
            "value": {
                "status": "success",
                "access_token": (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl"
                    "bWFpbCI6ImFjdGl2ZUB0ZXN0LmNvbSIsImV4cCI6M"
                    "TcxNjM2OTg4OCwidHlwZSI6ImFjY2VzcyJ9.YT-50"
                    "7Qo9oncWKKRJhRXBbpLrOCYoJOMxbk1IaAQef4"
                ),
                "refresh_token": (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl"
                    "bWFpbCI6ImFjdGl2ZUB0ZXN0LmNvbSIsImV4cCI6M"
                    "TcyMTU1MzEzNSwidHlwZSI6InJlZnJlc2gifQ._kc"
                    "SHTzcngWIt-LRX6yBx8ftpekT_Dqo8qbPyfgFjSQ"
                ),
            },
        },
    },
)
def refresh_token():
    """Refresh access and refresh tokens

    When access token is expired, call this resource using the refresh token to get a
    new pair of tokens.

    As opposed to all other resources, this resource must be accessed using the refresh
    token, not the access token.
    """
    user = get_current_user()
    return {
        "status": "success",
        "access_token": auth.encode(user).decode("utf-8"),
        "refresh_token": auth.encode(user, token_type="refresh").decode("utf-8"),
    }
