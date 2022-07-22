import marshmallow as ma
import enum

import pytest

from bemserver_api.extensions.ma_fields import Timezone, EnumField


class TestMaFields:
    def test_ma_fields_timezone(self):
        field = Timezone()
        assert field.deserialize("UTC") == "UTC"
        assert field.deserialize("Europe/Paris") == "Europe/Paris"
        with pytest.raises(ma.ValidationError):
            field.deserialize("Dordogne/Boulazac")

    def test_ma_fields_enumfield(self):
        class ThingsThatBurn(enum.Enum):
            wood = "wood"
            bridges = "bridges"
            witches = "witches"

        class ThingsThatFloat(enum.Enum):
            ducks = "ducks"
            bread = "bread"
            apples = "apples"
            very_small_rocks = "very_small_rocks"

        class Burn:
            thing = ThingsThatBurn.witches

        field = EnumField(ThingsThatBurn)

        burn = Burn()
        assert field.serialize("thing", burn) == "witches"
        burn.thing = ThingsThatFloat.ducks
        with pytest.raises(ma.ValidationError):
            field.serialize("thing", burn)

        assert field.deserialize("witches") == ThingsThatBurn.witches
        with pytest.raises(ma.ValidationError):
            field.deserialize(None)
        with pytest.raises(ma.ValidationError):
            field.deserialize(ThingsThatBurn.witches)
        with pytest.raises(ma.ValidationError):
            field.deserialize(ThingsThatFloat.very_small_rocks)

        field.allow_none = True
        assert field.deserialize(None) is None

        class BurnSchema(ma.Schema):
            thing = EnumField(ThingsThatBurn)

        burn_schema = BurnSchema()
        assert burn_schema.load({"thing": "witches"}) == {
            "thing": ThingsThatBurn.witches
        }
        with pytest.raises(ma.ValidationError):
            burn_schema.load({"thing": "ducks"})

        burn.thing = ThingsThatBurn.witches
        assert burn_schema.dump(burn) == {"thing": "witches"}
        burn.thing = ThingsThatFloat.ducks
        with pytest.raises(ma.ValidationError):
            burn_schema.dump(burn)
        burn.thing = "whatever_but_an_enum"
        with pytest.raises(ma.ValidationError):
            burn_schema.dump(burn)
