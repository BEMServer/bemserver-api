"""About API schemas"""
import marshmallow as ma

from bemserver_api import Schema


class VersionsSchema(Schema):
    bemserver_core = ma.fields.Str()
    bemserver_api = ma.fields.Str()


class AboutSchema(Schema):
    versions = ma.fields.Nested(VersionsSchema)
