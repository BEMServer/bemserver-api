"""Custom marshmallow fields"""
from pathlib import Path
import json

import marshmallow as ma


TIMEZONES_FILE = Path(__file__).parent / "timezones.json"


with open(TIMEZONES_FILE, encoding="utf-8") as tz_f:
    TIMEZONES = json.load(tz_f)


class Timezone(ma.fields.String):
    """A timezone field

    Validates timezone string is in the list of allowed timezones
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        validator = ma.validate.OneOf(TIMEZONES)
        self.validators.insert(0, validator)
