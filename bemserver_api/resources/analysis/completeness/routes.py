"""Completeness resources"""
from flask_smorest import abort

from bemserver_core.process.completeness import compute_completeness
from bemserver_core.model import Timeseries, TimeseriesDataState
from bemserver_core.exceptions import TimeseriesNotFoundError


from bemserver_api import Blueprint

from .schemas import CompletenessSchema, CompletenessQueryArgsSchema


blp = Blueprint(
    "Completeness",
    __name__,
    url_prefix="/completeness",
    description="Completness operations",
)


@blp.route("")
@blp.login_required
@blp.etag
@blp.arguments(CompletenessQueryArgsSchema, location="query")
@blp.response(200, CompletenessSchema)
def get_completeness(args):
    """Get timeseries data completeness

    Returns a report about data completeness, involving the number of values
    per time bucket and the sample interval.

    If the theoretical time interval for a timeseries is not defined in database,
    it is inferred from the maximum number of values per bucket.
    """
    try:
        timeseries = Timeseries.get_many_by_id(args["timeseries"])
    except TimeseriesNotFoundError as exc:
        abort(422, message=str(exc))
    if (data_state := TimeseriesDataState.get_by_id(args["data_state"])) is None:
        abort(422, errors={"query": {"data_state": "Unknown data state ID"}})

    completeness = compute_completeness(
        args["start_time"],
        args["end_time"],
        timeseries,
        data_state,
        args["bucket_width_value"],
        args["bucket_width_unit"],
        timezone=args["timezone"],
    )

    return completeness
