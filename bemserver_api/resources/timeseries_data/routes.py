"""Timeseries resources"""
import io

from flask import Response
from flask_smorest import abort

from bemserver_core.model import Campaign
from bemserver_core.csv_io import tscsvio
from bemserver_core.authorization import CurrentCampaign
from bemserver_core.exceptions import TimeseriesCSVIOError

from bemserver_api import Blueprint
from bemserver_api.resources.campaigns import blp as campaigns_blp

from .schemas import (
    TimeseriesDataQueryArgsSchema,
    TimeseriesDataAggregateQueryArgsSchema,
    TimeseriesCSVFileSchema,
)


blp = Blueprint(
    'TimeseriesData',
    __name__,
    url_prefix='/timeseries-data',
    description="Operations on timeseries data"
)


@blp.route('/', methods=('GET', ))
@blp.login_required
@blp.arguments(TimeseriesDataQueryArgsSchema, location='query')
@blp.response(200)
def get_csv(args):
    """Get timeseries data as CSV file"""
    csv_str = tscsvio.export_csv(
        args['start_time'],
        args['end_time'],
        args['timeseries']
    )

    response = Response(csv_str, mimetype='text/csv')
    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename="timeseries.csv"
    )
    return response


@blp.route('/aggregate', methods=('GET', ))
@blp.login_required
@blp.arguments(TimeseriesDataAggregateQueryArgsSchema, location='query')
@blp.response(200)
def get_aggregate_csv(args):
    """Get aggregated timeseries data as CSV file"""
    csv_str = tscsvio.export_csv_bucket(
        args['start_time'],
        args['end_time'],
        args['timeseries'],
        args['bucket_width'],
        args['timezone'],
        args['aggregation'],
    )

    response = Response(csv_str, mimetype='text/csv')
    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename="timeseries.csv"
    )
    return response


# TODO: document response
# https://github.com/marshmallow-code/flask-smorest/issues/142
@blp.route('/', methods=('POST', ))
@blp.login_required
@blp.arguments(TimeseriesCSVFileSchema, location='files')
@blp.response(201)
def post_csv(files):
    """Post timeseries data as CSV file"""
    csv_file = files['csv_file']
    with io.TextIOWrapper(csv_file) as csv_file_txt:
        try:
            tscsvio.import_csv(csv_file_txt)
        except TimeseriesCSVIOError:
            abort(422, "Invalid csv file content")


@campaigns_blp.route('/<int:campaign_id>/timeseries_data/', methods=('GET', ))
@campaigns_blp.login_required
@campaigns_blp.arguments(TimeseriesDataQueryArgsSchema, location='query')
@campaigns_blp.response(200)
def get_csv_for_campaign(args, campaign_id):
    """Get timeseries data as CSV file"""
    campaign = Campaign.get_by_id(campaign_id)
    if campaign is None:
        abort(404)
    with CurrentCampaign(campaign):
        csv_str = tscsvio.export_csv(
            args['start_time'],
            args['end_time'],
            args['timeseries'],
        )

    response = Response(csv_str, mimetype='text/csv')
    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename="timeseries.csv"
    )
    return response


@campaigns_blp.route(
    '/<int:campaign_id>/timeseries_data/aggregate', methods=('GET', ))
@campaigns_blp.login_required
@campaigns_blp.arguments(
    TimeseriesDataAggregateQueryArgsSchema, location='query')
@campaigns_blp.response(200)
def get_aggregate_csv_for_campaign(args, campaign_id):
    """Get aggregated timeseries data as CSV file"""
    campaign = Campaign.get_by_id(campaign_id)
    if campaign is None:
        abort(404)
    with CurrentCampaign(campaign):
        csv_str = tscsvio.export_csv_bucket(
            args['start_time'],
            args['end_time'],
            args['timeseries'],
            args['bucket_width'],
            args['timezone'],
            args['aggregation'],
        )

    response = Response(csv_str, mimetype='text/csv')
    response.headers.set(
        "Content-Disposition",
        "attachment",
        filename="timeseries.csv"
    )
    return response


# TODO: document response
# https://github.com/marshmallow-code/flask-smorest/issues/142
@campaigns_blp.route('/<int:campaign_id>/timeseries_data/', methods=('POST', ))
@campaigns_blp.login_required
@campaigns_blp.arguments(TimeseriesCSVFileSchema, location='files')
@campaigns_blp.response(201)
def post_csv_for_campaign(files, campaign_id):
    """Post timeseries data as CSV file"""
    campaign = Campaign.get_by_id(campaign_id)
    if campaign is None:
        abort(404)
    csv_file = files['csv_file']
    with CurrentCampaign(campaign):
        with io.TextIOWrapper(csv_file) as csv_file_txt:
            try:
                tscsvio.import_csv(csv_file_txt)
            except TimeseriesCSVIOError:
                abort(422, "Invalid csv file content")
