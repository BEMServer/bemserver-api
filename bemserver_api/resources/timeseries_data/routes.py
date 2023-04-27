"""Timeseries data resources"""
from textwrap import dedent

import flask
from flask_smorest import abort

from bemserver_core.model import Timeseries, TimeseriesDataState, Campaign
from bemserver_core.input_output import tsdio, tsdcsvio, tsdjsonio
from bemserver_core.database import db
from bemserver_core.exceptions import (
    TimeseriesNotFoundError,
    TimeseriesDataIOError,
    BEMServerCoreDimensionalityError,
)

from bemserver_api import Blueprint

from .schemas import (
    TimeseriesDataGetStatsByIDBaseQueryArgsSchema,
    TimeseriesDataGetStatsByNameBaseQueryArgsSchema,
    TimeseriesDataStatsByIDSchema,
    TimeseriesDataStatsByNameSchema,
    TimeseriesDataGetByIDQueryArgsSchema,
    TimeseriesDataDeleteByIDQueryArgsSchema,
    TimeseriesDataGetByNameQueryArgsSchema,
    TimeseriesDataDeleteByNameQueryArgsSchema,
    TimeseriesDataGetByIDAggregateQueryArgsSchema,
    TimeseriesDataGetByNameAggregateQueryArgsSchema,
    TimeseriesDataPostQueryArgsSchema,
)


STATS_BY_ID_EXAMPLE = dedent(
    """\
    {
        "stats":
        {
            "1": {
                "first_timestamp": "2020-01-01T00:00:00+00:00",
                "last_timestamp": "2021-01-01T00:00:00+00:00",
                "count": 42,
                "min": 0.0,
                "max": 42.0,
                "avg": 12.0,
                "stddev": 4.2,
            },
            "2": {
                "first_timestamp": "2020-01-01T00:00:00+00:00",
                "last_timestamp": "2021-01-01T00:00:00+00:00",
                "count": 69,
                "min": 12.0,
                "max": 142.0,
                "avg": 69.0,
                "stddev": 6.9,
            },
        },
    }"""
)


STATS_BY_NAME_EXAMPLE = dedent(
    """\
    {
        "stats":
        {
            "Timeseries 1": {
                "first_timestamp": "2020-01-01T00:00:00+00:00",
                "last_timestamp": "2021-01-01T00:00:00+00:00",
                "count": 42,
                "min": 0.0,
                "max": 42.0,
                "avg": 12.0,
                "stddev": 4.2,
            },
            "Timeseries 2": {
                "first_timestamp": "2020-01-01T00:00:00+00:00",
                "last_timestamp": "2021-01-01T00:00:00+00:00",
                "count": 69,
                "min": 12.0,
                "max": 142.0,
                "avg": 69.0,
                "stddev": 6.9,
            },
        },
    }"""
)


PAYLOAD_BY_ID_JSON_EXAMPLE = dedent(
    """\
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
    }"""
)

PAYLOAD_BY_ID_CSV_EXAMPLE = dedent(
    """\
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3"""
)

PAYLOAD_BY_NAME_JSON_EXAMPLE = dedent(
    """\
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
    }"""
)

PAYLOAD_BY_NAME_CSV_EXAMPLE = dedent(
    """\
    Datetime,Timeseries 1,Timeseries 2,Timeseries 3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3"""
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


@blp.route("/stats", methods=("GET",))
@blp.login_required
@blp.arguments(TimeseriesDataGetStatsByIDBaseQueryArgsSchema, location="query")
@blp.response(200, TimeseriesDataStatsByIDSchema, example=STATS_BY_ID_EXAMPLE)
def get_stats(args):
    """Get timeseries data stats"""
    timeseries = _get_many_timeseries_by_id(args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    data_df = tsdio.get_timeseries_stats(
        timeseries,
        data_state,
        timezone=args["timezone"],
        col_label="id",
    )

    return {
        "stats": data_df.astype(object)
        .where(data_df.notnull(), None)
        .to_dict(orient="index")
    }


@blp.route("/", methods=("GET",))
@blp.login_required
@blp.arguments(TimeseriesDataGetByIDQueryArgsSchema, location="query")
@blp.response(200, content_type="application/json", example=PAYLOAD_BY_ID_JSON_EXAMPLE)
@blp.alt_response(200, content_type="text/csv", example=PAYLOAD_BY_ID_CSV_EXAMPLE)
def get(args):
    """Get timeseries data

    Returns data in either JSON or CSV format.

    JSON: each key is a timestamp ID as string. For each timeseries, values are
    passed a {timestamp: value} mappings.

    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries IDs.
    """
    mime_type = flask.request.headers.get("Accept", "application/json")

    timeseries = _get_many_timeseries_by_id(args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    try:
        if mime_type == "text/csv":
            resp = tsdcsvio.export_csv(
                args["start_time"],
                args["end_time"],
                timeseries,
                data_state,
                convert_to=args.get("convert_to"),
                timezone=args["timezone"],
                col_label="id",
            )
        else:
            resp = tsdjsonio.export_json(
                args["start_time"],
                args["end_time"],
                timeseries,
                data_state,
                convert_to=args.get("convert_to"),
                timezone=args["timezone"],
                col_label="id",
            )
    except BEMServerCoreDimensionalityError as exc:
        abort(422, message=str(exc))

    return flask.Response(resp, mimetype=mime_type)


@blp.route("/aggregate", methods=("GET",))
@blp.login_required
@blp.arguments(TimeseriesDataGetByIDAggregateQueryArgsSchema, location="query")
@blp.response(200, content_type="application/json", example=PAYLOAD_BY_ID_JSON_EXAMPLE)
@blp.alt_response(200, content_type="text/csv", example=PAYLOAD_BY_ID_CSV_EXAMPLE)
def get_aggregate(args):
    """Get aggregated timeseries data as CSV file

    Returns data in either JSON or CSV format.

    JSON: each key is a timestamp ID as string. For each timeseries, values are
    passed a {timestamp: value} mappings.

    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries IDs.
    """
    mime_type = flask.request.headers.get("Accept", "application/json")

    timeseries = _get_many_timeseries_by_id(args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    if mime_type == "text/csv":
        resp = tsdcsvio.export_csv_bucket(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            args["bucket_width_value"],
            args["bucket_width_unit"],
            args["aggregation"],
            convert_to=args.get("convert_to"),
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
            convert_to=args.get("convert_to"),
            timezone=args["timezone"],
            col_label="id",
        )

    return flask.Response(resp, mimetype=mime_type)


@blp.route("/", methods=("POST",))
@blp.login_required
@blp.arguments(TimeseriesDataPostQueryArgsSchema, location="query")
@blp.doc(
    requestBody={
        "content": {
            "application/json": {
                "schema": {
                    "type": "string",
                    "format": "binary",
                    "example": PAYLOAD_BY_ID_JSON_EXAMPLE,
                }
            },
            "text/csv": {
                "schema": {
                    "type": "string",
                    "format": "binary",
                    "example": PAYLOAD_BY_ID_CSV_EXAMPLE,
                }
            },
        }
    }
)
@blp.response(201)
def post(args):
    """Post timeseries data

    Loads data in either JSON or CSV format.

    JSON: each key is a timestamp ID as string. For each timeseries, values are
    passed as {timestamp: value} mappings.
    """
    mime_type = flask.request.headers.get("content-type", "application/json")

    data_state = _get_data_state(args["data_state"])

    try:
        data = flask.request.get_data(cache=True).decode("utf-8")
    except UnicodeDecodeError as exc:
        abort(422, message=str(exc))

    try:
        if mime_type == "text/csv":
            tsdcsvio.import_csv(data, data_state)
        else:
            tsdjsonio.import_json(data, data_state)
    except (TimeseriesNotFoundError, TimeseriesDataIOError) as exc:
        abort(422, message=str(exc))

    db.session.commit()


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

    db.session.commit()


@blp4c.route("/stats", methods=("GET",))
@blp4c.login_required
@blp4c.arguments(TimeseriesDataGetStatsByNameBaseQueryArgsSchema, location="query")
@blp4c.response(200, TimeseriesDataStatsByNameSchema, example=STATS_BY_NAME_EXAMPLE)
def get_stats_for_campaign(args, campaign_id):
    """Get timeseries data stats"""
    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    timeseries = _get_many_timeseries_by_name(campaign, args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    data_df = tsdio.get_timeseries_stats(
        timeseries,
        data_state,
        timezone=args["timezone"],
        col_label="name",
    )

    return {
        "stats": data_df.astype(object)
        .where(data_df.notnull(), None)
        .to_dict(orient="index")
    }


@blp4c.route("/", methods=("GET",))
@blp4c.login_required
@blp4c.arguments(TimeseriesDataGetByNameQueryArgsSchema, location="query")
@blp4c.response(
    200, content_type="application/json", example=PAYLOAD_BY_NAME_JSON_EXAMPLE
)
@blp4c.alt_response(200, content_type="text/csv", example=PAYLOAD_BY_NAME_CSV_EXAMPLE)
def get_for_campaign(args, campaign_id):
    """Get timeseries data for a given campaign

    Returns data in either JSON or CSV format.

    JSON: each key is a timestamp name as string. For each timeseries, values
    are passed a {timestamp: value} mappings.

    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries names.
    """
    mime_type = flask.request.headers.get("Accept", "application/json")

    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    timeseries = _get_many_timeseries_by_name(campaign, args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    try:
        if mime_type == "text/csv":
            resp = tsdcsvio.export_csv(
                args["start_time"],
                args["end_time"],
                timeseries,
                data_state,
                convert_to=args.get("convert_to"),
                timezone=args["timezone"],
                col_label="name",
            )
        else:
            resp = tsdjsonio.export_json(
                args["start_time"],
                args["end_time"],
                timeseries,
                data_state,
                convert_to=args.get("convert_to"),
                timezone=args["timezone"],
                col_label="name",
            )
    except BEMServerCoreDimensionalityError as exc:
        abort(422, message=str(exc))

    return flask.Response(resp, mimetype=mime_type)


@blp4c.route("/aggregate", methods=("GET",))
@blp4c.login_required
@blp4c.arguments(TimeseriesDataGetByNameAggregateQueryArgsSchema, location="query")
@blp4c.response(
    200, content_type="application/json", example=PAYLOAD_BY_NAME_JSON_EXAMPLE
)
@blp4c.alt_response(200, content_type="text/csv", example=PAYLOAD_BY_NAME_CSV_EXAMPLE)
def get_aggregate_for_campaign(args, campaign_id):
    """Get aggregated timeseries data for a given campaign

    Returns data in either JSON or CSV format.

    JSON: each key is a timestamp name as string. For each timeseries, values
    are passed a {timestamp: value} mappings.

    CSV: the first column is the timestamp as timezone aware datetime and each
    other column is a timeseries data. Column headers are timeseries names.
    """
    mime_type = flask.request.headers.get("Accept", "application/json")

    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    timeseries = _get_many_timeseries_by_name(campaign, args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    if mime_type == "text/csv":
        resp = tsdcsvio.export_csv_bucket(
            args["start_time"],
            args["end_time"],
            timeseries,
            data_state,
            args["bucket_width_value"],
            args["bucket_width_unit"],
            args["aggregation"],
            convert_to=args.get("convert_to"),
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
            convert_to=args.get("convert_to"),
            timezone=args["timezone"],
            col_label="name",
        )

    return flask.Response(resp, mimetype=mime_type)


@blp4c.route("/", methods=("POST",))
@blp4c.login_required
@blp4c.arguments(TimeseriesDataPostQueryArgsSchema, location="query")
@blp4c.doc(
    requestBody={
        "content": {
            "application/json": {
                "schema": {
                    "type": "string",
                    "format": "binary",
                    "example": PAYLOAD_BY_NAME_JSON_EXAMPLE,
                }
            },
            "text/csv": {
                "schema": {
                    "type": "string",
                    "format": "binary",
                    "example": PAYLOAD_BY_NAME_CSV_EXAMPLE,
                }
            },
        }
    }
)
@blp4c.response(201)
def post_for_campaign(args, campaign_id):
    """Post timeseries data for a given campaign

    Loads data in either JSON or CSV format.

    JSON: each key is a timestamp ID as string. For each timeseries, values are
    passed as {timestamp: value} mappings.
    """
    mime_type = flask.request.headers.get("content-type", "application/json")

    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    data_state = _get_data_state(args["data_state"])

    try:
        data = flask.request.get_data(cache=True).decode("utf-8")
    except UnicodeDecodeError as exc:
        abort(422, message=str(exc))

    try:
        if mime_type == "text/csv":
            tsdcsvio.import_csv(data, data_state, campaign=campaign)
        else:
            tsdjsonio.import_json(data, data_state, campaign=campaign)
    except (TimeseriesNotFoundError, TimeseriesDataIOError) as exc:
        abort(422, message=str(exc))

    db.session.commit()


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

    db.session.commit()
