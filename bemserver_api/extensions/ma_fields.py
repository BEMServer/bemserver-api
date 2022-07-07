"""Custom marshmallow fields"""
import zoneinfo

import marshmallow as ma

from bemserver_core.input_output.timeseries_data_io import INTERVAL_UNITS


class Timezone(ma.fields.String):
    """A IANA timezone field.

    :param args: The same positional arguments that :class:`String` receives.
    :param kwargs: The same keyword arguments that :class:`String` receives.
    """

    #: Default error messages.
    default_error_messages = {"invalid": "Not a valid IANA timezone."}

    def _deserialize(self, value, attr, data, **kwargs):
        ret = super()._deserialize(value, attr, data, **kwargs)
        if ret not in zoneinfo.available_timezones():
            raise self.make_error("invalid")
        return ret


BUCKET_WIDTH_EXAMPLES = [
    "1 year",
    "2 month",
    "3 week",
    "4 day",
    "5 hour",
    "6 minute",
    "7 second",
]


class BucketWidth(ma.fields.String):
    """A field validating bucket widths"""

    #: Default error messages.
    default_error_messages = {"invalid": "Not a valid bucket width."}

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("metadata", {})
        kwargs["metadata"].setdefault("description", "Bucket width")
        kwargs["metadata"].setdefault("examples", BUCKET_WIDTH_EXAMPLES)
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        ret = super()._deserialize(value, attr, data, **kwargs)
        try:
            val, unit = ret.split()
            val = int(val)
        except ValueError as exc:
            raise self.make_error("invalid") from exc
        if unit not in INTERVAL_UNITS:
            raise self.make_error("invalid")
        if val < 1:
            raise self.make_error("invalid")
        return ret
