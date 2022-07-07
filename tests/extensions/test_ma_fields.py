import marshmallow as ma

import pytest

from bemserver_api.extensions.ma_fields import Timezone


class TestMaFields:
    def test_ma_fields_timezone(self):
        field = Timezone()
        assert field.deserialize("UTC") == "UTC"
        assert field.deserialize("Europe/Paris") == "Europe/Paris"
        with pytest.raises(ma.ValidationError):
            field.deserialize("Dordogne/Boulazac")
