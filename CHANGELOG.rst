Changelog
---------

0.5.0 (2022-12-15)
++++++++++++++++++

Features:

- Event API: replace level_id foreign key with level enum
- Event API: add level_min and in_source query args
- Timeseries API: add event_id query arg

Other changes:

- Require bemserver-core 0.4.0.

0.4.0 (2022-12-09)
++++++++++++++++++

Features:

- EventBySite, EventByBuilding,... resources.
- Remove PUT endpoint in TimeseriesByEvent resources.

Other changes:

- Require bemserver-core 0.3.0.

0.3.0 (2022-12-06)
++++++++++++++++++

Features:

- Event resources.
- Check missing data scheduled task.
- Hardcode ``API_VERSION`` and ``OPENAPI_VERSION``.
- Set ``API_VERSION`` as ``bemserver_api.__version__``.

Bug fixes:

- Fix ``API_VERSION``.

Other changes:

- Require bemserver-core 0.2.1.
- Support Python 3.11.


0.2.0 (2022-11-30)
++++++++++++++++++

Features:

- Timeseries data IO: provide JSON I/O.
- Timeseries data IO: improve error handling.
- Timeseries data IO: data in request/response body.

Other changes:

- Require bemserver-core 0.2.

0.1.0 (2022-11-18)
++++++++++++++++++

Features:

- Support bemserver-core 0.1.
