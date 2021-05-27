"""Timeseries tests"""
DUMMY_ID = '69'

TIMESERIES_URL = '/timeseries/'


class TestTimeseriesApi:

    def test_timeseries_api(self, app):

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_URL)
        assert ret.status_code == 200
        assert ret.json == []

        # POST
        timeseries_1 = {
            'name': 'Timeseries 1',
            'description': 'Timeseries example 1'
        }
        ret = client.post(TIMESERIES_URL, json=timeseries_1)
        assert ret.status_code == 201
        ret_val = ret.json
        timeseries_1_id = ret_val.pop('id')
        timeseries_1_etag = ret.headers['ETag']
        assert ret_val == timeseries_1

        # POST violating unique constraint
        ret = client.post(TIMESERIES_URL, json=timeseries_1)
        assert ret.status_code == 409

        # GET list
        ret = client.get(TIMESERIES_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]['id'] == timeseries_1_id

        # GET by id
        ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
        assert ret.status_code == 200
        assert ret.headers['ETag'] == timeseries_1_etag
        ret_val = ret.json
        ret_val.pop('id')
        assert ret_val == timeseries_1

        # PUT
        del timeseries_1['description']
        ret = client.put(
            f"{TIMESERIES_URL}{timeseries_1_id}",
            json=timeseries_1,
            headers={'If-Match': timeseries_1_etag}
        )
        assert ret.status_code == 200
        ret_val = ret.json
        ret_val.pop('id')
        timeseries_1_etag = ret.headers['ETag']
        assert ret_val == timeseries_1

        # PUT wrong ID -> 404
        ret = client.put(
            f"{TIMESERIES_URL}{DUMMY_ID}",
            json=timeseries_1,
            headers={'If-Match': timeseries_1_etag}
        )
        assert ret.status_code == 404

        # POST TS 2
        timeseries_2 = {
            'name': 'Timeseries 2',
        }
        ret = client.post(TIMESERIES_URL, json=timeseries_2)
        ret_val = ret.json
        timeseries_2_id = ret_val.pop('id')
        timeseries_2_etag = ret.headers['ETag']

        # PUT violating unique constraint
        timeseries_2['name'] = timeseries_1['name']
        ret = client.put(
            f"{TIMESERIES_URL}{timeseries_2_id}",
            json=timeseries_2,
            headers={'If-Match': timeseries_2_etag}
        )
        assert ret.status_code == 409

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_URL}{timeseries_1_id}",
            headers={'If-Match': timeseries_1_etag}
        )
        assert ret.status_code == 204
        ret = client.delete(
            f"{TIMESERIES_URL}{timeseries_2_id}",
            headers={'If-Match': timeseries_2_etag}
        )

        # GET list
        ret = client.get(TIMESERIES_URL)
        assert ret.status_code == 200
        assert ret.json == []

        # GET by id -> 404
        ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
        assert ret.status_code == 404
