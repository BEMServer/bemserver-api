import marshmallow as ma

import pytest

from bemserver_api.extensions.ma_fields import Timezone, BucketWidth


class TestMaFields:
    def test_ma_fields_timezone(self):
        field = Timezone()
        assert field.deserialize("UTC") == "UTC"
        assert field.deserialize("Europe/Paris") == "Europe/Paris"
        with pytest.raises(ma.ValidationError):
            field.deserialize("Dordogne/Boulazac")

    @pytest.mark.parametrize(
        "in_data",
        (
            "1 second",
            "2 minute",
            "3 hour",
            "4 day",
            "5 week",
            "42 month",
            "69 year",
        ),
    )
    def test_ma_fields_bucket_width_pass(self, in_data):
        field = BucketWidth()
        assert field.deserialize(in_data) == in_data

    @pytest.mark.parametrize(
        "in_data",
        (
            "lol",
            "12",
            "1.6 hour",
            "month",
            "1 test",
            '{"whatever": "nonsense"}',
        ),
    )
    def test_ma_fields_bucket_width_fail(self, in_data):
        field = BucketWidth()
        with pytest.raises(ma.ValidationError):
            field.deserialize(in_data)
