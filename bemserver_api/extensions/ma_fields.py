"""Custom marshmallow fields"""
import pytz

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
        if ret not in pytz.all_timezones:
            raise self.make_error("invalid")
        return ret


class BucketWidth(ma.fields.String):
    """A field validating bucket widths"""

    #: Default error messages.
    default_error_messages = {"invalid": "Not a valid bucket width."}

    def _deserialize(self, value, attr, data, **kwargs):
        ret = super()._deserialize(value, attr, data, **kwargs)
        try:
            val, unit = ret.split()
            int(val)
        except ValueError as exc:
            raise self.make_error("invalid") from exc
        if unit not in INTERVAL_UNITS:
            raise self.make_error("invalid")
        return ret
