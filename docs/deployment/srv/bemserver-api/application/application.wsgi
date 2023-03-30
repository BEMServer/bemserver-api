import os
from pathlib import Path

# Path to Celery settings file
# Must be set before import
os.environ["BEMSERVER_CELERY_SETTINGS_FILE"] = str(
    Path(__file__).parent.resolve() / "bemserver-celery-settings.py"
)

from bemserver_api import create_app  # noqa: E402

os.environ["BEMSERVER_CORE_SETTINGS_FILE"] = str(
    Path(__file__).parent.resolve() / "bemserver-core-settings.py"
)
os.environ["BEMSERVER_API_SETTINGS_FILE"] = str(
    Path(__file__).parent.resolve() / "bemserver-api-settings.py"
)

application = create_app()
