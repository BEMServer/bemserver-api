"""Process resources"""
from flask_smorest import abort

from bemserver_core.process.completeness import compute_completeness
from bemserver_core.model import Timeseries, TimeseriesDataState, Campaign
from bemserver_core.exceptions import TimeseriesNotFoundError


from bemserver_api import Blueprint

from .schemas import CompletenessSchema, CompletenessQueryArgsSchema


blp4c = Blueprint(
    "AnalysisForCampaign",
    __name__,
    url_prefix="/analysis/campaign/<int:campaign_id>",
    description="Data analysis operations for a given campaign",
)


@blp4c.route("/completeness")
@blp4c.login_required
@blp4c.etag
@blp4c.arguments(CompletenessQueryArgsSchema, location="query")
@blp4c.response(200, CompletenessSchema)
def get(args, campaign_id):
    """Get timeseries data completeness

    Returns a report about data completeness, involving the number of values
    per time bucket and the sample interval.

    If the theoretical time interval for a timeseries is not defined in database,
    it is inferred from the maximum number of values per bucket.
    """
    campaign = Campaign.get_by_id(campaign_id) or abort(404)
    try:
        timeseries = Timeseries.get_many_by_name(campaign, args["timeseries"])
    except TimeseriesNotFoundError as exc:
        abort(422, message=str(exc))
    if (data_state := TimeseriesDataState.get_by_id(args["data_state"])) is None:
        abort(422, errors={"query": {"data_state": "Unknown data state ID"}})

    completeness = compute_completeness(
        args["start_time"],
        args["end_time"],
        timeseries,
        data_state,
        args["bucket_width"],
        timezone=args["timezone"],
    )

    return completeness
