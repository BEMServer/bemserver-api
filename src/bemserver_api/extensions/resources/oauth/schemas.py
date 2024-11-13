import marshmallow as ma

from bemserver_api import Schema


class OauthGetJWTArgsSchema(Schema):
    token = ma.fields.String(validate=ma.validate.Length(1, 80), required=True)


class OauthCallbackArgsSchema(Schema):
    code = ma.fields.String(validate=ma.validate.Length(1, 80), required=True)


class OauthGetJWTRespSchema(Schema):
    status = ma.fields.String(validate=ma.validate.OneOf(("success", "failure")))
    access_token = ma.fields.String()
    refresh_token = ma.fields.String()
