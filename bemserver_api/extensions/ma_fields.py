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
