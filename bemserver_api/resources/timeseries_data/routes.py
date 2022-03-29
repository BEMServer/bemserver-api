"""Timeseries data resources"""
import io
import textwrap

from flask import Response
from flask_smorest import abort

from bemserver_core.csv_io import tscsvio
from bemserver_core.exceptions import TimeseriesCSVIOError

from bemserver_api import Blueprint

from .schemas import (
    TimeseriesDataGetQueryArgsSchema,
    TimeseriesDataGetAggregateQueryArgsSchema,
    TimeseriesDataPostQueryArgsSchema,
    TimeseriesDataPostFileSchema,
)


EXAMPLE_CSV_IN_OUT_FILE = textwrap.dedent(
    """\
    Datetime,1,2,3
    2020-01-01T00:00:00+00:00,0.1,1.1,2.1
    2020-01-01T00:10:00+00:00,0.2,1.2,2.2
    2020-01-01T00:20:00+00:00,0.3,1.3,2.3
    """
)


blp = Blueprint(
    "TimeseriesData",
    __name__,
    url_prefix="/timeseries_data",
    description="Operations on timeseries data",
)


@blp.route("/", methods=("GET",))
@blp.login_required
@blp.arguments(TimeseriesDataGetQueryArgsSchema, location="query")
@blp.response(
    200,
    {"format": "binary", "type": "string"},
    content_type="application/csv",
    example=EXAMPLE_CSV_IN_OUT_FILE,
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

    csv_str = tscsvio.export_csv(
        args["start_time"],
        args["end_time"],
        args["timeseries"],
        args["data_state"],
    )
    response = Response(csv_str, mimetype="text/csv")
    response.headers.set("Content-Disposition", "attachment", filename="timeseries.csv")
    return response


@blp.route("/aggregate", methods=("GET",))
@blp.login_required
@blp.arguments(TimeseriesDataGetAggregateQueryArgsSchema, location="query")
@blp.response(
    200,
    {"format": "binary", "type": "string"},
    content_type="application/csv",
    example=EXAMPLE_CSV_IN_OUT_FILE,
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
    csv_str = tscsvio.export_csv_bucket(
        args["start_time"],
        args["end_time"],
        args["timeseries"],
        args["data_state"],
        args["bucket_width"],
        args["timezone"],
        args["aggregation"],
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
    csv_file = files["csv_file"]
    with io.TextIOWrapper(csv_file) as csv_file_txt:
        try:
            tscsvio.import_csv(csv_file_txt, args["data_state"])
        except TimeseriesCSVIOError:
            abort(422, "Invalid csv file content")
