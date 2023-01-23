import os
from pathlib import Path

from bemserver_api import create_app

os.environ["FLASK_SETTINGS_FILE"] = str(
    Path(__file__).parent.resolve() / "settings.cfg"
)

application = create_app()
