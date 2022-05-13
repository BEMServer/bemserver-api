"""Input/Output resources"""
import io

from flask_smorest import abort

from bemserver_core.model import Campaign
from bemserver_core.input_output import sites_csv_io

from bemserver_api import Blueprint
from bemserver_core.exceptions import SitesCSVIOError


from .schemas import SitesCSVUploadQueryArgsSchema, SitesCSVUploadFileSchema


blp = Blueprint(
    "Input/Output", __name__, url_prefix="/io", description="Input/Output operations"
)


@blp.post("/sites")
@blp.login_required
@blp.arguments(SitesCSVUploadQueryArgsSchema, location="query")
@blp.arguments(SitesCSVUploadFileSchema, location="files")
@blp.response(201)
def sites_csv_io_post(args, files):
    """Import site description tree"""
    campaign_id = args["campaign_id"]
    csv_files = {
        k: io.TextIOWrapper(v, encoding="utf-8")
        for k, v in files.items()
        if v is not None
    }

    campaign = Campaign.get_by_id(campaign_id)
    if campaign is None:
        abort(422, errors={"query": {"campaign_id": ["Unknown campaign ID."]}})
    try:
        sites_csv_io.import_csv(campaign=campaign, **csv_files)
    except SitesCSVIOError as exc:
        abort(422, message=f"Invalid csv file content: {exc}")
