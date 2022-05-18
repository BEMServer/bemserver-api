"""Input/Output API schemas"""
import marshmallow as ma
from flask_smorest.fields import Upload

from bemserver_api import Schema


class SitesCSVUploadQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int(required=True)


class SitesCSVUploadFileSchema(Schema):
    sites_csv = Upload()
    buildings_csv = Upload()
    storeys_csv = Upload()
    spaces_csv = Upload()
    zones_csv = Upload()


class TimeseriesCSVUploadQueryArgsSchema(Schema):
    campaign_id = ma.fields.Int(required=True)


class TimeseriesCSVUploadFileSchema(Schema):
    timeseries_csv = Upload(required=True)
