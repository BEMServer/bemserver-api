"""Custom marshmallow fields"""
import zoneinfo

import marshmallow as ma


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
