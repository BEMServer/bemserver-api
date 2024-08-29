import marshmallow as ma

from bemserver_api import Schema


class GetJWTArgsSchema(Schema):
    email = ma.fields.Email(required=True)
    password = ma.fields.String(validate=ma.validate.Length(1, 80), required=True)


class GetJWTRespSchema(Schema):
    status = ma.fields.String(validate=ma.validate.OneOf(("success", "failure")))
    access_token = ma.fields.String()
    refresh_token = ma.fields.String()
