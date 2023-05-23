"""Energy consumption tests"""
from copy import deepcopy
import datetime as dt
import contextlib

import pandas as pd

import pytest

from bemserver_core.database import db
from bemserver_core.model import (
    UserGroupByCampaignScope,
    Timeseries,
    TimeseriesDataState,
    Energy,
    EnergyEndUse,
    EnergyConsumptionTimeseriesBySite,
    EnergyConsumptionTimeseriesByBuilding,
)
from bemserver_core.authorization import OpenBar

from tests.common import AuthHeader
from tests.utils import create_timeseries_data


ENERGY_CONSUMPTION_URL = "/analysis/energy_consumption/"


class TestAnalysisApiEnergyConsumption:
    def _create_data(self, campaign_id, campaign_scope_id):
        start_dt = dt.datetime(2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
        end_dt = dt.datetime(2020, 1, 1, 2, 0, tzinfo=dt.timezone.utc)

        timestamps = pd.date_range(start_dt, end_dt, inclusive="left", freq="H")

        # Create timeseries and timeseries data
        ds_clean = TimeseriesDataState.get(name="Clean").first()

        timeseries = []
        for i in range(9):
            ts_i = Timeseries(
                name=f"Timeseries {i+1}",
                campaign_id=campaign_id,
                campaign_scope_id=campaign_scope_id,
                unit_symbol=("Wh" if i < 6 else "kWh"),
            )
            timeseries.append(ts_i)
        db.session.add_all(timeseries)
        db.session.flush()

        create_timeseries_data(timeseries[0], ds_clean, timestamps, [71, 71])
        create_timeseries_data(timeseries[1], ds_clean, timestamps, [46, 46])
        create_timeseries_data(timeseries[2], ds_clean, timestamps, [25, 25])
        create_timeseries_data(timeseries[3], ds_clean, timestamps, [50, 50])
        create_timeseries_data(timeseries[4], ds_clean, timestamps, [25, 25])
        create_timeseries_data(timeseries[5], ds_clean, timestamps, [25, 25])
        create_timeseries_data(timeseries[6], ds_clean, timestamps, [0.021, 0.021])
        create_timeseries_data(timeseries[7], ds_clean, timestamps, [0.021, 0.021])

        expected_consumptions_wh = {
            "all": {
                "all": [71.0, 71.0],
                "heating": [46.0, 46.0],
                "cooling": [25.0, 25.0],
            },
            "electricity": {
                "all": [50.0, 50.0],
                "heating": [25.0, 25.0],
                "cooling": [25.0, 25.0],
            },
            "natural gas": {
                "all": [21.0, 21.0],
                "heating": [21.0, 21.0],
                "cooling": [0.0, 0.0],
            },
        }

        expected_consumptions_mwh = deepcopy(expected_consumptions_wh)
        for energy in expected_consumptions_mwh.values():
            for usage in energy.keys():
                energy[usage] = [val * 1000 for val in energy[usage]]

        expected_consumptions_wh_ratio_2 = deepcopy(expected_consumptions_wh)
        for energy in expected_consumptions_wh_ratio_2.values():
            for usage in energy.keys():
                energy[usage] = [val / 2 for val in energy[usage]]

        timestamps = [ts.isoformat() for ts in timestamps.to_list()]

        expected = {
            "Wh": {
                "timestamps": timestamps,
                "energy": expected_consumptions_wh,
            },
            "mWh": {
                "timestamps": timestamps,
                "energy": expected_consumptions_mwh,
            },
            "Wh_ratio_2": {
                "timestamps": timestamps,
                "energy": expected_consumptions_wh_ratio_2,
            },
        }

        return start_dt, end_dt, timeseries, expected

    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.usefixtures("site_property_data")
    def test_analysis_energy_consumption_breakdown_for_site(
        self,
        app,
        user,
        users,
        campaigns,
        campaign_scopes,
        sites,
        timeseries,
    ):
        campaign_1_id = campaigns[0]
        cs_1_id = campaign_scopes[0]
        site_1_id = sites[0]

        if user == "admin":
            creds = users["Chuck"]["creds"]
            auth_context = AuthHeader(creds)
        elif user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
        else:
            auth_context = contextlib.nullcontext()

        client = app.test_client()

        query_url = f"{ENERGY_CONSUMPTION_URL}site/{site_1_id}"

        with OpenBar():
            start_time, end_time, timeseries, expected = self._create_data(
                campaign_1_id, cs_1_id
            )

            energy_all = Energy.get(name="all").first()
            energy_elec = Energy.get(name="electricity").first()
            energy_gas = Energy.get(name="natural gas").first()
            end_use_all = EnergyEndUse.get(name="all").first()
            end_use_heating = EnergyEndUse.get(name="heating").first()
            end_use_cooling = EnergyEndUse.get(name="cooling").first()

            ectbs_all_all = EnergyConsumptionTimeseriesBySite.new(
                site_id=sites[0],
                energy_id=energy_all.id,
                end_use_id=end_use_all.id,
                timeseries_id=timeseries[0].id,
            )
            ectbs_all_heating = EnergyConsumptionTimeseriesBySite.new(
                site_id=sites[0],
                energy_id=energy_all.id,
                end_use_id=end_use_heating.id,
                timeseries_id=timeseries[1].id,
            )
            ectbs_all_cooling = EnergyConsumptionTimeseriesBySite.new(
                site_id=sites[0],
                energy_id=energy_all.id,
                end_use_id=end_use_cooling.id,
                timeseries_id=timeseries[2].id,
            )
            ectbs_elec_all = EnergyConsumptionTimeseriesBySite.new(
                site_id=sites[0],
                energy_id=energy_elec.id,
                end_use_id=end_use_all.id,
                timeseries_id=timeseries[3].id,
            )
            ectbs_elec_heating = EnergyConsumptionTimeseriesBySite.new(
                site_id=sites[0],
                energy_id=energy_elec.id,
                end_use_id=end_use_heating.id,
                timeseries_id=timeseries[4].id,
            )
            ectbs_elec_cooling = EnergyConsumptionTimeseriesBySite.new(
                site_id=sites[0],
                energy_id=energy_elec.id,
                end_use_id=end_use_cooling.id,
                timeseries_id=timeseries[5].id,
            )
            ectbs_gas_all = EnergyConsumptionTimeseriesBySite.new(
                site_id=sites[0],
                energy_id=energy_gas.id,
                end_use_id=end_use_all.id,
                timeseries_id=timeseries[6].id,
            )
            ectbs_gas_heating = EnergyConsumptionTimeseriesBySite.new(
                site_id=sites[0],
                energy_id=energy_gas.id,
                end_use_id=end_use_heating.id,
                timeseries_id=timeseries[7].id,
            )
            ectbs_gas_cooling = EnergyConsumptionTimeseriesBySite.new(
                site_id=sites[0],
                energy_id=energy_gas.id,
                end_use_id=end_use_cooling.id,
                timeseries_id=timeseries[8].id,
            )
            db.session.add_all(
                (
                    ectbs_all_all,
                    ectbs_all_heating,
                    ectbs_all_cooling,
                    ectbs_elec_all,
                    ectbs_elec_heating,
                    ectbs_elec_cooling,
                    ectbs_gas_all,
                    ectbs_gas_heating,
                    ectbs_gas_cooling,
                )
            )
            db.session.commit()

        with auth_context:
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == expected["Wh"]

            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "unit": "mWh",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == expected["mWh"]

        # Wrong unit
        with auth_context:
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                    "unit": "°C",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 409
                ret_data = ret.json
                assert ret_data["message"] == "Incompatible unit in input timeseries."

        # Ratio
        with auth_context:
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                    "ratio_property": "Area",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == expected["Wh_ratio_2"]

        # Wrong ratio (no value or unknown property)
        with auth_context:
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                    "ratio_property": "Dummy",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 409
                ret_data = ret.json
                assert ret_data["message"] == 'Site has no "Dummy" property.'

        # Without user <-> timeseries association
        with OpenBar():
            ugbcs_1 = UserGroupByCampaignScope.get(campaign_scope_id=cs_1_id).first()
            ugbcs_1.delete()
            db.session.commit()

        with auth_context:
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                # User can't read consumption data from unauthorized timeseries
                expected["Wh"]["energy"] = {}
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == expected["Wh"]
            else:
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == expected["Wh"]

    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.usefixtures("building_property_data")
    def test_analysis_energy_consumption_breakdown_for_building(
        self,
        app,
        user,
        users,
        campaigns,
        campaign_scopes,
        buildings,
        timeseries,
    ):
        campaign_1_id = campaigns[0]
        cs_1_id = campaign_scopes[0]
        building_1_id = buildings[0]

        if user == "admin":
            creds = users["Chuck"]["creds"]
            auth_context = AuthHeader(creds)
        elif user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
        else:
            auth_context = contextlib.nullcontext()

        client = app.test_client()

        query_url = f"{ENERGY_CONSUMPTION_URL}building/{building_1_id}"

        with OpenBar():
            start_time, end_time, timeseries, expected = self._create_data(
                campaign_1_id, cs_1_id
            )

            energy_all = Energy.get(name="all").first()
            energy_elec = Energy.get(name="electricity").first()
            energy_gas = Energy.get(name="natural gas").first()
            end_use_all = EnergyEndUse.get(name="all").first()
            end_use_heating = EnergyEndUse.get(name="heating").first()
            end_use_cooling = EnergyEndUse.get(name="cooling").first()

            ectbs_all_all = EnergyConsumptionTimeseriesByBuilding.new(
                building_id=buildings[0],
                energy_id=energy_all.id,
                end_use_id=end_use_all.id,
                timeseries_id=timeseries[0].id,
            )
            ectbs_all_heating = EnergyConsumptionTimeseriesByBuilding.new(
                building_id=buildings[0],
                energy_id=energy_all.id,
                end_use_id=end_use_heating.id,
                timeseries_id=timeseries[1].id,
            )
            ectbs_all_cooling = EnergyConsumptionTimeseriesByBuilding.new(
                building_id=buildings[0],
                energy_id=energy_all.id,
                end_use_id=end_use_cooling.id,
                timeseries_id=timeseries[2].id,
            )
            ectbs_elec_all = EnergyConsumptionTimeseriesByBuilding.new(
                building_id=buildings[0],
                energy_id=energy_elec.id,
                end_use_id=end_use_all.id,
                timeseries_id=timeseries[3].id,
            )
            ectbs_elec_heating = EnergyConsumptionTimeseriesByBuilding.new(
                building_id=buildings[0],
                energy_id=energy_elec.id,
                end_use_id=end_use_heating.id,
                timeseries_id=timeseries[4].id,
            )
            ectbs_elec_cooling = EnergyConsumptionTimeseriesByBuilding.new(
                building_id=buildings[0],
                energy_id=energy_elec.id,
                end_use_id=end_use_cooling.id,
                timeseries_id=timeseries[5].id,
            )
            ectbs_gas_all = EnergyConsumptionTimeseriesByBuilding.new(
                building_id=buildings[0],
                energy_id=energy_gas.id,
                end_use_id=end_use_all.id,
                timeseries_id=timeseries[6].id,
            )
            ectbs_gas_heating = EnergyConsumptionTimeseriesByBuilding.new(
                building_id=buildings[0],
                energy_id=energy_gas.id,
                end_use_id=end_use_heating.id,
                timeseries_id=timeseries[7].id,
            )
            ectbs_gas_cooling = EnergyConsumptionTimeseriesByBuilding.new(
                building_id=buildings[0],
                energy_id=energy_gas.id,
                end_use_id=end_use_cooling.id,
                timeseries_id=timeseries[8].id,
            )
            db.session.add_all(
                (
                    ectbs_all_all,
                    ectbs_all_heating,
                    ectbs_all_cooling,
                    ectbs_elec_all,
                    ectbs_elec_heating,
                    ectbs_elec_cooling,
                    ectbs_gas_all,
                    ectbs_gas_heating,
                    ectbs_gas_cooling,
                )
            )
            db.session.commit()

        with auth_context:
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == expected["Wh"]

            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "unit": "mWh",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == expected["mWh"]

        # Wrong unit
        with auth_context:
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                    "unit": "°C",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 409
                ret_data = ret.json
                assert ret_data["message"] == "Incompatible unit in input timeseries."

        # Ratio
        with auth_context:
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                    "ratio_property": "Area",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == expected["Wh_ratio_2"]

        # Wrong ratio (no value or unknown property)
        with auth_context:
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                    "ratio_property": "Dummy",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 409
                ret_data = ret.json
                assert ret_data["message"] == 'Building has no "Dummy" property.'

        # Without user <-> timeseries association
        with OpenBar():
            timeseries[0].unit_symbol = "Wh"
            db.session.add(timeseries[0])
            ugbcs_1 = UserGroupByCampaignScope.get(campaign_scope_id=cs_1_id).first()
            ugbcs_1.delete()
            db.session.commit()

        with auth_context:
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                # User can't read consumption data from unauthorized timeseries
                expected["Wh"]["energy"] = {}
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == expected["Wh"]
            else:
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == expected["Wh"]
