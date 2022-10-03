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


class EnumField(ma.fields.Field):
    """Marshmallow field for enum type."""

    #: Default error messages.
    default_error_messages = {
        "invalid_value": "Not a valid enum value.",
        "invalid_name": "Not a valid enum name.",
    }

    def __init__(self, enum_obj, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enum_obj = enum_obj

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize an enum value to a string"""
        if not isinstance(value, self._enum_obj):
            raise self.make_error("invalid_value")
        ret = super()._serialize(value, attr, obj, **kwargs)
        return ret.name

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize a string to an enum value"""
        ret = super()._deserialize(value, attr, data, **kwargs)
        try:
            return self._enum_obj[ret]
        except KeyError:
            raise self.make_error("invalid_name")
