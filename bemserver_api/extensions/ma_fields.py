"""Custom marshmallow fields"""
from pathlib import Path
import datetime as dt
import json

import marshmallow as ma
from webargs.fields import DelimitedList

from bemserver_core.common import ureg
from bemserver_core.exceptions import BEMServerCoreUndefinedUnitError


TIMEZONES_FILE = Path(__file__).parent / "timezones.json"


with open(TIMEZONES_FILE, encoding="utf-8") as tz_f:
    TIMEZONES = json.load(tz_f)


# https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
# Timestamp limitations
# Since pandas represents timestamps in nanosecond resolution, the time span that
# can be represented using a 64-bit integer is limited to approximately 584 years:
# pd.Timestamp.min: Timestamp('1677-09-21 00:12:43.145224193')
# pd.Timestamp.max: Timestamp('2262-04-11 23:47:16.854775807')
DATETIME_RANGE_VALIDATOR = ma.validate.Range(
    dt.datetime(1680, 1, 1, tzinfo=dt.timezone.utc),
    dt.datetime(2260, 1, 1, tzinfo=dt.timezone.utc),
)


class AwareDateTime(ma.fields.AwareDateTime):
    """A timezone aware datetime field

    Rejects datetimes that can't be converted to pandas timestamps
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(DATETIME_RANGE_VALIDATOR)


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


class SortField(DelimitedList):
    """Field used to specify sort order fields

    :param list fields: List of fields to sort upon, by order of priority (the
    first field is the first sort key). Each field is a field name, optionally
    prefixed with "+" or "-".
    """

    def __init__(self, fields, **kwargs):
        validator = ma.validate.OneOf(
            [v for f in fields for v in [f, f"+{f}", f"-{f}"]]
        )
        super().__init__(ma.fields.String(validate=validator), **kwargs)
