"""Timeseries data resources"""
import io
import textwrap

from flask import Response
from flask_smorest import abort

from bemserver_core.model import Timeseries, TimeseriesDataState, Campaign
from bemserver_core.input_output import tsdcsvio
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
    TimeseriesDataPostFileSchema,
)


EXAMPLE_CSV_IN_OUT_FILE_TS_ID = textwrap.dedent(
    """\
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    """
)

EXAMPLE_CSV_IN_OUT_FILE_TS_NAME = textwrap.dedent(
    """\
    Datetime,Timeseries 1,Timeseries 2,Timeseries 3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    """
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
@blp.response(
    200,
    {"format": "binary", "type": "string"},
    content_type="application/csv",
    example=EXAMPLE_CSV_IN_OUT_FILE_TS_ID,
)
def get_csv(args):
    """Get timeseries data as CSV file

    Returns a CSV file where the first column is the timestamp as timezone aware
    datetime and each other column is a timeseries data. Column headers are
    timeseries IDs.

    ```
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    timeseries = _get_many_timeseries_by_id(args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    csv_str = tsdcsvio.export_csv(
        args["start_time"],
        args["end_time"],
        timeseries,
        data_state,
        timezone=args["timezone"],
        col_label="id",
    )
    response = Response(csv_str, mimetype="text/csv")
    response.headers.set("Content-Disposition", "attachment", filename="timeseries.csv")
    return response


@blp.route("/aggregate", methods=("GET",))
@blp.login_required
@blp.arguments(TimeseriesDataGetByIDAggregateQueryArgsSchema, location="query")
@blp.response(
    200,
    {"format": "binary", "type": "string"},
    content_type="application/csv",
    example=EXAMPLE_CSV_IN_OUT_FILE_TS_ID,
)
def get_aggregate_csv(args):
    """Get aggregated timeseries data as CSV file

    Returns a CSV file where the first column is the timestamp as timezone aware
    datetime and each other column is a timeseries data. Column headers are
    timeseries IDs.

    ```
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    timeseries = _get_many_timeseries_by_id(args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    csv_str = tsdcsvio.export_csv_bucket(
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
    response = Response(csv_str, mimetype="text/csv")
    response.headers.set("Content-Disposition", "attachment", filename="timeseries.csv")
    return response


@blp.route("/", methods=("POST",))
@blp.login_required
@blp.arguments(TimeseriesDataPostFileSchema, location="files")
@blp.arguments(TimeseriesDataPostQueryArgsSchema, location="query")
@blp.response(201)
def post_csv(files, args):
    """Post timeseries data as CSV file

    Loads a CSV file where the first column is the timestamp as timezone aware
    datetime and each other column is a timeseries data. Column headers are
    timeseries ID.

    ```
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    data_state = _get_data_state(args["data_state"])

    with io.TextIOWrapper(files["csv_file"], encoding="utf-8") as csv_file_txt:
        try:
            tsdcsvio.import_csv(csv_file_txt, data_state)
        except (TimeseriesNotFoundError, TimeseriesDataIOError) as exc:
            abort(422, message=f"Invalid CSV file content: {exc}")


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
@blp4c.response(
    200,
    {"format": "binary", "type": "string"},
    content_type="application/csv",
    example=EXAMPLE_CSV_IN_OUT_FILE_TS_NAME,
)
def get_csv_for_campaign(args, campaign_id):
    """Get timeseries data as CSV file for a given campaign

    Returns a CSV file where the first column is the timestamp as timezone aware
    datetime and each other column is a timeseries data. Column headers are
    timeseries IDs.

    ```
    Datetime,Timeseries 1,Timeseries 2,Timeseries 3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    timeseries = _get_many_timeseries_by_name(campaign, args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    csv_str = tsdcsvio.export_csv(
        args["start_time"],
        args["end_time"],
        timeseries,
        data_state,
        timezone=args["timezone"],
        col_label="name",
    )
    response = Response(csv_str, mimetype="text/csv")
    response.headers.set("Content-Disposition", "attachment", filename="timeseries.csv")
    return response


@blp4c.route("/aggregate", methods=("GET",))
@blp4c.login_required
@blp4c.arguments(TimeseriesDataGetByNameAggregateQueryArgsSchema, location="query")
@blp4c.response(
    200,
    {"format": "binary", "type": "string"},
    content_type="application/csv",
    example=EXAMPLE_CSV_IN_OUT_FILE_TS_NAME,
)
def get_aggregate_csv_for_campaign(args, campaign_id):
    """Get aggregated timeseries data as CSV file for a given campaign

    Returns a CSV file where the first column is the timestamp as timezone aware
    datetime and each other column is a timeseries data. Column headers are
    timeseries IDs.

    ```
    Datetime,Timeseries 1,Timeseries 2,Timeseries 3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    timeseries = _get_many_timeseries_by_name(campaign, args["timeseries"])
    data_state = _get_data_state(args["data_state"])

    csv_str = tsdcsvio.export_csv_bucket(
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
    response = Response(csv_str, mimetype="text/csv")
    response.headers.set("Content-Disposition", "attachment", filename="timeseries.csv")
    return response


@blp4c.route("/", methods=("POST",))
@blp4c.login_required
@blp4c.arguments(TimeseriesDataPostFileSchema, location="files")
@blp4c.arguments(TimeseriesDataPostQueryArgsSchema, location="query")
@blp4c.response(201)
def post_csv_for_campaign(files, args, campaign_id):
    """Post timeseries data as CSV file for a given campaign

    Loads a CSV file where the first column is the timestamp as timezone aware
    datetime and each other column is a timeseries data. Column headers are
    timeseries ID.

    ```
    Datetime,Timeseries 1,Timeseries 2,Timeseries 3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    ```
    """
    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    data_state = _get_data_state(args["data_state"])

    with io.TextIOWrapper(files["csv_file"], encoding="utf-8") as csv_file_txt:
        try:
            tsdcsvio.import_csv(csv_file_txt, data_state, campaign=campaign)
        except (TimeseriesNotFoundError, TimeseriesDataIOError) as exc:
            abort(422, message=f"Invalid CSV file content: {exc}")


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
