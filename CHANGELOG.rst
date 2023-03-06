Changelog
---------

0.14.0 (2023-03-06)
+++++++++++++++++++

Features:

- Reject all datetimes before 1680 or after 2260 to avoid pandas issues
- Embed Timeseries in WeatherTimeseriesBySite response

Other changes:

- Require bemserver-core 0.11.1
- Require apispec 6.1.0

0.13.1 (2023-03-03)
+++++++++++++++++++

Bug fixes:

- Fix GET Energy Consumption/ProductionTimeseriesBySite/Building query arguments

0.13.0 (2023-03-01)
+++++++++++++++++++

Features:

- Rename EnergySource -> Energy
- EnergyProductionTechnology API
- EnergyProductionTimeseriesBySite/Building API
- Embed Timeseries in EnergyConsumption/ProductionTimeseriesBySite/Building response
- WeatherTimeseriesBySite API

Other changes:

- Require bemserver-core 0.11.0

0.12.1 (2023-03-01)
+++++++++++++++++++

Bug fixes:

- Fix error messages returned with 409 responses on integrity errors
- Catch BEMServerCoreDimensionalityError when computing energy consumption
  breakdown to return a 409 with meaningful error instead of a 500

0.12.0 (2023-02-28)
+++++++++++++++++++

Features:

- Validate unit symbols in timeseries and properties
- Remove wh_conversion_factor from EnergyConsumptionTimeseriesBySite/Building

Other changes:

- Require bemserver-core 0.10.1
- Require SQLAlchemy 2.0

0.11.1 (2023-02-10)
+++++++++++++++++++

Features:

- Embed Timeseries and Event in TimeseriesByEvent response

0.11.0 (2023-02-09)
+++++++++++++++++++

Other changes:

- Require bemserver-core 0.9.1

0.10.3 (2023-02-03)
+++++++++++++++++++

Features:

- Embed Event in Notification response

0.10.2 (2023-02-01)
+++++++++++++++++++

Bug fixes:

- Fix Notification mark_all_as_read: PUT, not GET

0.10.1 (2023-02-01)
+++++++++++++++++++

Features:

- Notification: add count_by_campaign and mark_all_as_read
- Add Notification campaign_id filter

Bug fixes:

- Fix server error when loading timeseries as CSV with wrong datetimes

Other changes:

- Require bemserver-core 0.8.1

0.10.0 (2023-01-17)
+++++++++++++++++++

Features:

- Check outliers data scheduled task

Other changes:

- Require bemserver-core 0.8.0

0.9.0 (2023-01-12)
++++++++++++++++++

Features:

- Remove PUT and ETag for association tables
- Add pagination in lists involving timeseries or events
- Add Site,... hierarchy to Site,... associations

0.8.0 (2023-01-11)
++++++++++++++++++

Features:

- Rework Timeseries event filter
- Rework Timeseries site,... filters
- Rework Event site,... filters
- Add Notifications query arguments

Other changes:

- Require bemserver-core 0.7.0

0.7.0 (2023-01-06)
++++++++++++++++++

Features:

- Manage invalid UTF-8 files in sites/timeseries IO
- Notification API
- EventCategoryByUser API

Other changes:

- Require bemserver-core 0.6.0

0.6.0 (2022-12-22)
++++++++++++++++++

Features:

- Split Timeseries site_id/... and event_id filters into separate routes
- Add Event campaign_id, user_id, timeseries_id and site_id/... filters

Other changes:

- Require bemserver-core 0.5.0

0.5.0 (2022-12-15)
++++++++++++++++++

Features:

- Event API: replace level_id foreign key with level enum
- Event API: add level_min and in_source query args
- Timeseries API: add event_id query arg

Other changes:

- Require bemserver-core 0.4.0

0.4.0 (2022-12-09)
++++++++++++++++++

Features:

- EventBySite, EventByBuilding,... resources
- Remove PUT endpoint in TimeseriesByEvent resources

Other changes:

- Require bemserver-core 0.3.0

0.3.0 (2022-12-06)
++++++++++++++++++

Features:

- Event resources
- Check missing data scheduled task
- Hardcode ``API_VERSION`` and ``OPENAPI_VERSION``
- Set ``API_VERSION`` as ``bemserver_api.__version__``

Bug fixes:

- Fix ``API_VERSION``

Other changes:

- Require bemserver-core 0.2.1
- Support Python 3.11


0.2.0 (2022-11-30)
++++++++++++++++++

Features:

- Timeseries data IO: provide JSON I/O
- Timeseries data IO: improve error handling
- Timeseries data IO: data in request/response body

Other changes:

- Require bemserver-core 0.2.0

0.1.0 (2022-11-18)
++++++++++++++++++

Features:

- Support bemserver-core 0.1.0
