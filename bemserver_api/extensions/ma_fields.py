"""Custom marshmallow fields"""
from pathlib import Path
import json

import marshmallow as ma

from bemserver_core.common import ureg
from bemserver_core.exceptions import BEMServerCoreUndefinedUnitError


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


class UnitSymbol(ma.fields.String):
    """A unit symbol field

    Validates unit is defined
    """

    def _deserialize(self, value, attr, data, **kwargs):
        value = super()._deserialize(value, attr, data, **kwargs)
        try:
            ureg.validate_unit(value)
        except BEMServerCoreUndefinedUnitError as exc:
            raise ma.ValidationError("Undefined unit.") from exc
        return value
