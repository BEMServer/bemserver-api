import os
from pathlib import Path

# Path to Celery settings file
# Must be set before import
os.environ["BEMSERVER_CELERY_SETTINGS_FILE"] = str(
    Path(__file__).parent.resolve() / "celery-settings.cfg"
)

from bemserver_api import create_app  # noqa: E402

os.environ["FLASK_SETTINGS_FILE"] = str(
    Path(__file__).parent.resolve() / "settings.cfg"
)

application = create_app()
