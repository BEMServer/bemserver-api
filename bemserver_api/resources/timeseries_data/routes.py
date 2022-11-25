"""Timeseries data resources"""
import flask
from flask_smorest import abort

from bemserver_core.model import Timeseries, TimeseriesDataState, Campaign
from bemserver_core.input_output import tsdcsvio, tsdjsonio
from bemserver_core.exceptions import (
    TimeseriesNotFoundError,
    TimeseriesDataIOError,
)

from bemserver_api import Blueprint

from .schemas import (
    TimeseriesDataGetByIDQueryArgsSchema,
    TimeseriesDataDeleteByIDQueryArgsSchema,
    TimeseriesDataGetByNameQueryArgsSchema,
    TimeseriesDataDeleteByNameQueryArgsSchema,
    TimeseriesDataGetByIDAggregateQueryArgsSchema,
    TimeseriesDataGetByNameAggregateQueryArgsSchema,
    TimeseriesDataPostQueryArgsSchema,
    TimeseriesDataGetAcceptHeader,
)


def _get_data_state(data_state_id):
    return TimeseriesDataState.get_by_id(data_state_id) or abort(
        422, errors={"query": {"data_state": "Unknown data state ID"}}
    )


def _get_many_timeseries_by_id(timeseries_ids):
    try:
        return Timeseries.get_many_by_id(timeseries_ids)
    except TimeseriesNotFoundError as exc:
        abort(422, message=str(exc))


def _get_many_timeseries_by_name(campaign, timeseries_ids):
    try:
        return Timeseries.get_many_by_name(campaign, timeseries_ids)
    except TimeseriesNotFoundError as exc:
        abort(422, message=str(exc))


blp = Blueprint(
    "TimeseriesData",
    __name__,
    url_prefix="/timeseries_data",
    description="Operations on timeseries data",
)


blp4c = Blueprint(
    "TimeseriesDataForCampaign",
    __name__,
    url_prefix="/timeseries_data/campaign/<int:campaign_id>",
    description="Operations on timeseries data for a given campaign",
)


@blp.route("/", methods=("GET",))
@blp.login_required
@blp.arguments(TimeseriesDataGetByIDQueryArgsSchema, location="query")
@blp.arguments(TimeseriesDataGetAcceptHeader, location="headers", error_status_code=406)
@blp.response(200, content_type="application/json")
@blp.alt_response(200, content_type="application/csv")
def get(args, headers):
    """Get timeseries data

    Returns data in either JSON or CSV format.

    JSON: each key is a timestamp ID as string. For each timeseries, values are
    passed a {timestamp: value} mappings.

    ```
    {
        "1": {
            "2020-01-01T00:00:00+00:00": 0.1,
            "2020-01-01T10:00:00+00:00": 0.2,
            "2020-01-01T20:00:00+00:00": 0.3,
        },
        "2": {
            "2020-01-01T00:00:00+00:00": 1.1,
            "2020-01-01T10:00:00+00:00": 1.2,
            "2020-01-01T20:00:00+00:00": 1.3,
        },
        "3": {
            "2020-01-01T00:00:00+00:00": 2.1,
            "2020-01-01T10:00:00+00:00": 2.2,
            "2020-01-01T20:00:00+00:00": 2.3,
        },
    }
    ```
    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries IDs.

    ```
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    mime_type = headers["accept"]

    timeseries = _get_many_timeseries_by_id(args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    if mime_type == "application/csv":
        resp = tsdcsvio.export_csv(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            timezone=args["timezone"],
            col_label="id",
        )
    else:
        resp = tsdjsonio.export_json(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            timezone=args["timezone"],
            col_label="id",
        )

    return flask.Response(resp, mimetype=mime_type)


@blp.route("/aggregate", methods=("GET",))
@blp.login_required
@blp.arguments(TimeseriesDataGetByIDAggregateQueryArgsSchema, location="query")
@blp.arguments(TimeseriesDataGetAcceptHeader, location="headers", error_status_code=406)
@blp.response(200, content_type="application/csv")
def get_aggregate(args, headers):
    """Get aggregated timeseries data as CSV file

    Returns data in either JSON or CSV format.

    JSON: each key is a timestamp ID as string. For each timeseries, values are
    passed a {timestamp: value} mappings.

    ```
    {
        "1": {
            "2020-01-01T00:00:00+00:00": 0.1,
            "2020-01-01T10:00:00+00:00": 0.2,
            "2020-01-01T20:00:00+00:00": 0.3,
        },
        "2": {
            "2020-01-01T00:00:00+00:00": 1.1,
            "2020-01-01T10:00:00+00:00": 1.2,
            "2020-01-01T20:00:00+00:00": 1.3,
        },
        "3": {
            "2020-01-01T00:00:00+00:00": 2.1,
            "2020-01-01T10:00:00+00:00": 2.2,
            "2020-01-01T20:00:00+00:00": 2.3,
        },
    }
    ```

    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries IDs.

    ```
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    mime_type = headers["accept"]

    timeseries = _get_many_timeseries_by_id(args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    if mime_type == "application/csv":
        resp = tsdcsvio.export_csv_bucket(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            args["bucket_width_value"],
            args["bucket_width_unit"],
            args["aggregation"],
            timezone=args["timezone"],
            col_label="id",
        )
    else:
        resp = tsdjsonio.export_json_bucket(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            args["bucket_width_value"],
            args["bucket_width_unit"],
            args["aggregation"],
            timezone=args["timezone"],
            col_label="id",
        )

    return flask.Response(resp, mimetype=mime_type)


@blp.route("/", methods=("POST",))
@blp.login_required
@blp.arguments(TimeseriesDataPostQueryArgsSchema, location="query")
@blp.arguments(TimeseriesDataGetAcceptHeader, location="headers", error_status_code=406)
@blp.response(201)
def post(args, headers):
    """Post timeseries data

    Loads data in either JSON or CSV format.

    JSON: each key is a timestamp ID as string. For each timeseries, values are
    passed a {timestamp: value} mappings.

    ```
    {
        "1": {
            "2020-01-01T00:00:00+00:00": 0.1,
            "2020-01-01T10:00:00+00:00": 0.2,
            "2020-01-01T20:00:00+00:00": 0.3,
        },
        "2": {
            "2020-01-01T00:00:00+00:00": 1.1,
            "2020-01-01T10:00:00+00:00": 1.2,
            "2020-01-01T20:00:00+00:00": 1.3,
        },
        "3": {
            "2020-01-01T00:00:00+00:00": 2.1,
            "2020-01-01T10:00:00+00:00": 2.2,
            "2020-01-01T20:00:00+00:00": 2.3,
        },
    }
    ```

    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries IDs.

    ```
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    mime_type = headers["accept"]

    data_state = _get_data_state(args["data_state"])

    try:
        data = flask.request.get_data(cache=True).decode("utf-8")
    except UnicodeDecodeError as exc:
        abort(422, message=str(exc))

    try:
        if mime_type == "application/csv":
            tsdcsvio.import_csv(data, data_state)
        else:
            tsdjsonio.import_json(data, data_state)
    except (TimeseriesNotFoundError, TimeseriesDataIOError) as exc:
        abort(422, message=str(exc))


@blp.route("/", methods=("DELETE",))
@blp.login_required
@blp.arguments(TimeseriesDataDeleteByIDQueryArgsSchema, location="query")
@blp.response(204)
def delete(args):
    """Delete timeseries data"""
    timeseries = _get_many_timeseries_by_id(args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    tsdcsvio.delete(
        args["start_time"],
        args["end_time"],
        timeseries,
        data_state,
    )


@blp4c.route("/", methods=("GET",))
@blp4c.login_required
@blp4c.arguments(TimeseriesDataGetByNameQueryArgsSchema, location="query")
@blp4c.arguments(
    TimeseriesDataGetAcceptHeader, location="headers", error_status_code=406
)
@blp4c.response(200, content_type="application/csv")
def get_for_campaign(args, headers, campaign_id):
    """Get timeseries data for a given campaign

    Returns data in either JSON or CSV format.

    JSON: each key is a timestamp name as string. For each timeseries, values
    are passed a {timestamp: value} mappings.

    ```
    {
        "Timeseries 1": {
            "2020-01-01T00:00:00+00:00": 0.1,
            "2020-01-01T10:00:00+00:00": 0.2,
            "2020-01-01T20:00:00+00:00": 0.3,
        },
        "Timeseries 2": {
            "2020-01-01T00:00:00+00:00": 1.1,
            "2020-01-01T10:00:00+00:00": 1.2,
            "2020-01-01T20:00:00+00:00": 1.3,
        },
        "Timeseries 3": {
            "2020-01-01T00:00:00+00:00": 2.1,
            "2020-01-01T10:00:00+00:00": 2.2,
            "2020-01-01T20:00:00+00:00": 2.3,
        },
    }
    ```

    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries names.

    ```
    Datetime,Timeseries 1,Timeseries 2,Timeseries 3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    mime_type = headers["accept"]

    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    timeseries = _get_many_timeseries_by_name(campaign, args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    if mime_type == "application/csv":
        resp = tsdcsvio.export_csv(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            timezone=args["timezone"],
            col_label="name",
        )
    else:
        resp = tsdjsonio.export_json(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            timezone=args["timezone"],
            col_label="name",
        )

    return flask.Response(resp, mimetype=mime_type)


@blp4c.route("/aggregate", methods=("GET",))
@blp4c.login_required
@blp4c.arguments(TimeseriesDataGetByNameAggregateQueryArgsSchema, location="query")
@blp4c.arguments(
    TimeseriesDataGetAcceptHeader, location="headers", error_status_code=406
)
@blp4c.response(200, content_type="application/csv")
def get_aggregate_for_campaign(args, headers, campaign_id):
    """Get aggregated timeseries data for a given campaign

    Returns data in either JSON or CSV format.

    JSON: each key is a timestamp name as string. For each timeseries, values
    are passed a {timestamp: value} mappings.

    ```
    {
        "Timeseries 1": {
            "2020-01-01T00:00:00+00:00": 0.1,
            "2020-01-01T10:00:00+00:00": 0.2,
            "2020-01-01T20:00:00+00:00": 0.3,
        },
        "Timeseries 2": {
            "2020-01-01T00:00:00+00:00": 1.1,
            "2020-01-01T10:00:00+00:00": 1.2,
            "2020-01-01T20:00:00+00:00": 1.3,
        },
        "Timeseries 3": {
            "2020-01-01T00:00:00+00:00": 2.1,
            "2020-01-01T10:00:00+00:00": 2.2,
            "2020-01-01T20:00:00+00:00": 2.3,
        },
    }
    ```

    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries names.

    ```
    Datetime,Timeseries 1,Timeseries 2,Timeseries 3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    mime_type = headers["accept"]

    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    timeseries = _get_many_timeseries_by_name(campaign, args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    if mime_type == "application/csv":
        resp = tsdcsvio.export_csv_bucket(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            args["bucket_width_value"],
            args["bucket_width_unit"],
            args["aggregation"],
            timezone=args["timezone"],
            col_label="name",
        )
    else:
        resp = tsdjsonio.export_json_bucket(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            args["bucket_width_value"],
            args["bucket_width_unit"],
            args["aggregation"],
            timezone=args["timezone"],
            col_label="name",
        )

    return flask.Response(resp, mimetype=mime_type)


@blp4c.route("/", methods=("POST",))
@blp4c.login_required
@blp4c.arguments(TimeseriesDataPostQueryArgsSchema, location="query")
@blp4c.arguments(
    TimeseriesDataGetAcceptHeader, location="headers", error_status_code=406
)
@blp4c.response(201)
def post_for_campaign(args, headers, campaign_id):
    """Post timeseries data for a given campaign

    Loads data in either JSON or CSV format.

    JSON: each key is a timestamp ID as string. For each timeseries, values are
    passed a {timestamp: value} mappings.

    ```
    {
        "1": {
            "2020-01-01T00:00:00+00:00": 0.1,
            "2020-01-01T10:00:00+00:00": 0.2,
            "2020-01-01T20:00:00+00:00": 0.3,
        },
        "2": {
            "2020-01-01T00:00:00+00:00": 1.1,
            "2020-01-01T10:00:00+00:00": 1.2,
            "2020-01-01T20:00:00+00:00": 1.3,
        },
        "3": {
            "2020-01-01T00:00:00+00:00": 2.1,
            "2020-01-01T10:00:00+00:00": 2.2,
            "2020-01-01T20:00:00+00:00": 2.3,
        },
    }
    ```

    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries IDs.

    ```
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    mime_type = headers["accept"]

    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    data_state = _get_data_state(args["data_state"])

    try:
        data = flask.request.get_data(cache=True).decode("utf-8")
    except UnicodeDecodeError as exc:
        abort(422, message=str(exc))

    try:
        if mime_type == "application/csv":
            tsdcsvio.import_csv(data, data_state, campaign=campaign)
        else:
            tsdjsonio.import_json(data, data_state, campaign=campaign)
    except (TimeseriesNotFoundError, TimeseriesDataIOError) as exc:
        abort(422, message=str(exc))


@blp4c.route("/", methods=("DELETE",))
@blp4c.login_required
@blp4c.arguments(TimeseriesDataDeleteByNameQueryArgsSchema, location="query")
@blp4c.response(204)
def delete_for_campaign(args, campaign_id):
    """Delete timeseries data for a given campaign"""
    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    timeseries = _get_many_timeseries_by_name(campaign, args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    tsdcsvio.delete(
        args["start_time"],
        args["end_time"],
        timeseries,
        data_state,
    )
