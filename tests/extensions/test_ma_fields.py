import marshmallow as ma

import pytest

from bemserver_api.extensions.ma_fields import Timezone, UnitSymbol


class TestMaFields:
    def test_ma_fields_timezone(self):
        field = Timezone()
        assert field.deserialize("UTC") == "UTC"
        assert field.deserialize("Europe/Paris") == "Europe/Paris"
        with pytest.raises(ma.ValidationError):
            field.deserialize("Dordogne/Boulazac")

    def test_ma_fields_unit_symbol(self):
        field = UnitSymbol()
        assert field.deserialize("") == ""
        assert field.deserialize("m") == "m"
        assert field.deserialize("meter") == "meter"
        assert field.deserialize("kWh") == "kWh"
        assert field.deserialize("m/s") == "m/s"
        assert field.deserialize("m3/m3") == "m3/m3"
        with pytest.raises(ma.ValidationError):
            field.deserialize("wh")
        with pytest.raises(ma.ValidationError):
            field.deserialize("dummy")
