"""Notifications tests"""
import datetime as dt

from tests.common import AuthHeader


DUMMY_ID = "69"

NOTIFICATIONS_URL = "/notifications/"


class TestNotificationsApi:
    def test_notifications_api(self, app, users, campaigns, events):
        creds = users["Chuck"]["creds"]
        user_1_id = users["Active"]["id"]
        user_2_id = users["Inactive"]["id"]
        campaign_1_id = campaigns[0]
        campaign_2_id = campaigns[1]
        event_1_id = events[0]
        event_2_id = events[1]

        dt_1 = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).isoformat()
        dt_2 = dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc).isoformat()

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(NOTIFICATIONS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val

            # POST
            notif_1 = {
                "event_id": event_1_id,
                "user_id": user_1_id,
                "timestamp": dt_1,
            }
            ret = client.post(NOTIFICATIONS_URL, json=notif_1)
            assert ret.status_code == 201
            ret_val = ret.json
            notif_1_id = ret_val.pop("id")
            assert "event" in ret_val
            assert "id" not in ret_val["event"]

            # GET list
            ret = client.get(NOTIFICATIONS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert "id" not in ret_val[0]["event"]

            # GET by id
            ret = client.get(f"{NOTIFICATIONS_URL}{notif_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val.pop("read") is False
            assert "id" not in ret_val.pop("event")
            assert ret_val == notif_1

            # PUT wrong ID -> 404
            notif_1_put = {
                "read": True,
            }
            ret = client.put(f"{NOTIFICATIONS_URL}{DUMMY_ID}", json=notif_1_put)
            assert ret.status_code == 404

            # PUT
            ret = client.put(
                f"{NOTIFICATIONS_URL}{notif_1_id}",
                json=notif_1_put,
            )
            assert ret.status_code == 200
            ret_val = ret.json

            # POST
            notif_2 = {
                "event_id": event_2_id,
                "user_id": user_2_id,
                "timestamp": dt_2,
            }
            ret = client.post(NOTIFICATIONS_URL, json=notif_2)
            ret_val = ret.json
            notif_2_id = ret_val["id"]

            # GET list
            ret = client.get(NOTIFICATIONS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(NOTIFICATIONS_URL, query_string={"user_id": user_1_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == notif_1_id
            ret = client.get(
                NOTIFICATIONS_URL, query_string={"campaign_id": campaign_1_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == notif_1_id
            ret = client.get(NOTIFICATIONS_URL, query_string={"read": True})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == notif_1_id
            ret = client.get(NOTIFICATIONS_URL, query_string={"timestamp_min": dt_2})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == notif_2_id
            ret = client.get(NOTIFICATIONS_URL, query_string={"timestamp_max": dt_1})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == notif_1_id

            # GET sorted list
            ret = client.get(NOTIFICATIONS_URL, query_string={"sort": "timestamp"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert ret_val[0]["id"] == notif_1_id
            ret = client.get(NOTIFICATIONS_URL, query_string={"sort": "-timestamp"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert ret_val[1]["id"] == notif_1_id

            # GET count by campaign
            ret = client.get(
                f"{NOTIFICATIONS_URL}count_by_campaign",
                query_string={"user_id": user_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert ret_val == {
                "campaigns": [
                    {"campaign_id": 1, "campaign_name": "Campaign 1", "count": 1}
                ],
                "total": 1,
            }
            ret = client.get(
                f"{NOTIFICATIONS_URL}count_by_campaign",
                query_string={"user_id": user_1_id, "read": False},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert ret_val == {"campaigns": [], "total": 0}

            # Mark all notifications as read
            notif_1_put["read"] = False
            ret = client.put(
                f"{NOTIFICATIONS_URL}{notif_1_id}",
                json=notif_1_put,
            )
            assert ret.status_code == 200
            # At this point, 2 notifs
            # User 1, Campaign 1, unread
            # User 2, Campaign 2, unread
            ret = client.get(NOTIFICATIONS_URL, query_string={"read": False})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            # Mark all user 1 notif as read -> no unread notif for user 1
            ret = client.put(
                f"{NOTIFICATIONS_URL}mark_all_as_read",
                query_string={"user_id": user_1_id},
            )
            assert ret.status_code == 204
            ret = client.get(
                NOTIFICATIONS_URL, query_string={"user_id": user_1_id, "read": False}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val
            # Mark all user 2 notif as read for campaign 1 -> no change
            # (User 2 is not even part of campaign 1, they couldn't have a notif there)
            ret = client.put(
                f"{NOTIFICATIONS_URL}mark_all_as_read",
                query_string={"user_id": user_2_id, "campaign_id": campaign_1_id},
            )
            assert ret.status_code == 204
            ret = client.get(
                NOTIFICATIONS_URL, query_string={"user_id": user_2_id, "read": False}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            # Mark all user 2 notif as read for campaign 2 -> no unread notif for user 2
            ret = client.put(
                f"{NOTIFICATIONS_URL}mark_all_as_read",
                query_string={"user_id": user_2_id, "campaign_id": campaign_2_id},
            )
            assert ret.status_code == 204
            ret = client.get(
                NOTIFICATIONS_URL, query_string={"user_id": user_2_id, "read": False}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val

            # DELETE wrong ID -> 404
            ret = client.delete(f"{NOTIFICATIONS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(f"{NOTIFICATIONS_URL}{notif_1_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(NOTIFICATIONS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1

            # GET by id -> 404
            ret = client.get(f"{NOTIFICATIONS_URL}{notif_1_id}")
            assert ret.status_code == 404

    def test_notifications_as_user_api(
        self, app, users, campaigns, events, notifications
    ):
        user_creds = users["Active"]["creds"]
        user_1_id = users["Active"]["id"]
        user_2_id = users["Inactive"]["id"]
        campaign_1_id = campaigns[0]
        campaign_2_id = campaigns[1]
        event_1_id = events[0]
        notif_1_id = notifications[0]
        notif_2_id = notifications[1]

        dt_1 = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).isoformat()

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(NOTIFICATIONS_URL)
            assert ret.status_code == 200

            # POST
            notif = {
                "event_id": event_1_id,
                "user_id": user_1_id,
                "timestamp": dt_1,
            }
            ret = client.post(NOTIFICATIONS_URL, json=notif)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{NOTIFICATIONS_URL}{notif_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            notif_1 = ret_val
            assert notif_1["read"] is False
            assert "id" not in ret_val.pop("event")

            ret = client.get(f"{NOTIFICATIONS_URL}{notif_2_id}")
            assert ret.status_code == 403

            # PUT - set read status
            notif_1_put = {
                "read": True,
            }
            ret = client.put(f"{NOTIFICATIONS_URL}{notif_1_id}", json=notif_1_put)
            assert ret.status_code == 200

            # GET count by campaign
            ret = client.get(
                f"{NOTIFICATIONS_URL}count_by_campaign",
                query_string={"user_id": user_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert ret_val == {
                "campaigns": [
                    {"campaign_id": 1, "campaign_name": "Campaign 1", "count": 1}
                ],
                "total": 1,
            }
            ret = client.get(
                f"{NOTIFICATIONS_URL}count_by_campaign",
                query_string={"user_id": user_1_id, "read": False},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert ret_val == {"campaigns": [], "total": 0}
            ret = client.get(
                f"{NOTIFICATIONS_URL}count_by_campaign",
                query_string={"user_id": user_2_id},
            )
            assert ret.status_code == 403

            # Mark all notifications as read
            notif_1_put["read"] = False
            ret = client.put(
                f"{NOTIFICATIONS_URL}{notif_1_id}",
                json=notif_1_put,
            )
            assert ret.status_code == 200
            # At this point, 1 notif
            # User 1, Campaign 1, unread
            # Mark all user 1 notif as read for campaign 2 -> no change
            ret = client.put(
                f"{NOTIFICATIONS_URL}mark_all_as_read",
                query_string={"user_id": user_1_id, "campaign_id": campaign_2_id},
            )
            assert ret.status_code == 204
            ret = client.get(
                NOTIFICATIONS_URL, query_string={"user_id": user_1_id, "read": False}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            # Mark all user 1 notif as read for campaign 1 -> no unread notif for user 1
            ret = client.put(
                f"{NOTIFICATIONS_URL}mark_all_as_read",
                query_string={"user_id": user_1_id, "campaign_id": campaign_1_id},
            )
            assert ret.status_code == 204
            ret = client.get(
                NOTIFICATIONS_URL, query_string={"user_id": user_2_id, "read": False}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val

            # DELETE
            ret = client.delete(f"{NOTIFICATIONS_URL}{notif_1_id}")
            assert ret.status_code == 403

    def test_notifications_as_anonym_api(self, app, users, events, notifications):
        user_1_id = users["Active"]["id"]
        event_1_id = events[0]
        notif_1_id = notifications[0]

        dt_1 = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).isoformat()

        client = app.test_client()

        # GET list
        ret = client.get(NOTIFICATIONS_URL)
        assert ret.status_code == 401

        # POST
        notif = {
            "event_id": event_1_id,
            "user_id": user_1_id,
            "timestamp": dt_1,
        }
        ret = client.post(NOTIFICATIONS_URL, json=notif)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{NOTIFICATIONS_URL}{notif_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(f"{NOTIFICATIONS_URL}{notif_1_id}", json=notif)

        # GET count by campaign
        ret = client.get(
            f"{NOTIFICATIONS_URL}count_by_campaign",
            query_string={"user_id": user_1_id},
        )
        assert ret.status_code == 401

        # Mark all notifications as read
        ret = client.get(
            f"{NOTIFICATIONS_URL}mark_all_as_read",
            query_string={"user_id": user_1_id},
        )
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{NOTIFICATIONS_URL}{notif_1_id}")
        assert ret.status_code == 401
